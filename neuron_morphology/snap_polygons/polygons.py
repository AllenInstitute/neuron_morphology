from typing import Tuple, Union

import pandas as pd
import numpy as np
import shapely
import shapely.geometry
from shapely.geometry.polygon import Polygon
import geopandas
import rasterio
import rasterio.features
import matplotlib.pyplot as plt
import skimage
import skimage.morphology


import allensdk.internal.core.lims_utilities as lu

def get_layer_drawings() -> pd.DataFrame:
    """ Annotaters draw polygons defining cortical layers on each sub image. This query 
    returns all such polygons.
    """

    qs = """
        select
            spp.id as parent_specimen_id,
            sp.id as specimen_id,
            st.acronym as structure_acronym,
            polygon.path as path,
            polygon.id as pid,
            label.name as label_name,
            si.id as sub_image_id,
            imser.id as image_series_id,
            im.height as height,
            im.width as width
        from specimens sp
        join specimens spp on spp.id = sp.parent_id
        join image_series imser on imser.specimen_id = spp.id
        join sub_images si on si.image_series_id = imser.id
        join images im on im.id = si.image_id
        join treatments tm on tm.id = im.treatment_id
        join avg_graphic_objects layer on layer.sub_image_id = si.id
        join avg_group_labels label on label.id = layer.group_label_id
        join avg_graphic_objects polygon on polygon.parent_id = layer.id
        join structures st on st.id = polygon.cortex_layer_id
        join neuron_reconstructions nr on nr.specimen_id = sp.id
        where 
            label.name in ('Cortical Layers')
            and nr.id is not null
            and not nr.superseded
            and nr.manual
            and tm.name = 'Biocytin' -- the polys are duplicated between 'Biocytin' and 'DAPI' images. Need only one of these
    """
    return pd.DataFrame(lu.query(qs))


def get_pia_wm_drawings():
    qs = """
        select 
            spp.id as parent_specimen_id,
            sp.id as specimen_id,
            polygon.path as path,
            polygon.id as id,
            label.name as label_name,
            si.id as sub_image_id,
            imser.id as image_series_id,
            im.height as height,
            im.width as width
        from specimens sp
        join specimens spp on spp.id = sp.parent_id
        join image_series imser on imser.specimen_id = spp.id
        join sub_images si on si.image_series_id = imser.id
        join images im on im.id = si.image_id
        join treatments tm on tm.id = im.treatment_id
        join avg_graphic_objects layer on layer.sub_image_id = si.id
        join avg_graphic_objects polygon on polygon.parent_id = layer.id
        join avg_group_labels label on label.id = layer.group_label_id
        join neuron_reconstructions nr on nr.specimen_id = sp.id
        where
            label.name in ('Pia', 'White Matter')
            and nr.id is not null
            and not nr.superseded
            and nr.manual
            and tm.name = 'Biocytin'
    """

    return pd.DataFrame(lu.query(qs))


def split_pathstring(pathstring: str, num_dims=2, sep=",") -> np.ndarray:
    """ Converts a pathstring ("x,y,x,y...") to a num_points X num_dims array of float
    """
    
    split = list(map(float, pathstring.split(sep)))
    divisions  = len(split) / num_dims
    
    if divisions - int(divisions):
        raise ValueError(f"unable to split {len(split)} long path among {num_dims} dimensions")
    
    return np.reshape(split, (int(divisions), num_dims))


class CorticalLayerDrawings:

    @property
    def xy_aspect_ratio(self):
        return self.xlen / self.ylen

    @property
    def ylen(self):
        return self.bounds[3] - self.bounds[1]

    @property
    def xlen(self):
        return self.bounds[2] - self.bounds[0]

    @property
    def names(self):
        return list(self.layer_polygons.keys())

    def __init__(self):
        """
        """

        self.in_shape = None
        self.bounds = None
        self.layer_polygons = {}

    def register_layer_polygon(self, name: str, path: Union[str, Polygon]):
        if isinstance(path, str):
            _path = split_pathstring(path)

            for_poly = [
                tuple(np.squeeze(item)) 
                for item 
                in np.split(_path, _path.shape[0], axis=0)
            ]
            polygon = shapely.geometry.polygon.Polygon(for_poly)
        elif isinstance(path, Polygon):
            polygon = path

        self.layer_polygons[name] = polygon
        self.update_bounds(*polygon.bounds)

    def update_bounds(self, minx, miny, maxx, maxy):
        if self.bounds is None:
            self.bounds = (minx, miny, maxx, maxy)
        else:
            self.bounds = (
                min(minx, self.bounds[0]),
                min(miny, self.bounds[1]),
                max(maxx, self.bounds[2]),
                max(maxy, self.bounds[3])
            )

    def rescale(self, new_shape: Tuple[int]):

        def _rescale(x, y):
            return (
                new_shape[0] * self.mmnormx(x), 
                new_shape[1] * self.mmnormy(y)
            )

        new = CorticalLayerDrawings()
        for name, polygon in self.layer_polygons.items():
            new.register_layer_polygon(
                name, shapely.ops.transform(_rescale, polygon)
            )

        return new

    def mmnormx(self, x):
        return (x - self.bounds[0]) / self.xlen
    
    def mmnormy(self, y):
        return (y - self.bounds[1]) / self.ylen

    def rasterize(self, out_shape: Union[Tuple, np.ndarray], names=None):

        if names is None:
            names = self.names

        return rasterio.features.rasterize([
            [self.layer_polygons[name], ii + 1]
            for ii, name 
            in enumerate(names)
        ], out_shape=out_shape[::-1])


if __name__ == "__main__":

    layer_drawings = {}
    for _specimen_id, group in get_layer_drawings().groupby("specimen_id"):
        layer_drawings[_specimen_id] = pd.DataFrame(group)

    pia_wm_drawings = {}
    for _specimen_id, group in get_pia_wm_drawings().groupby("specimen_id"):
        pia_wm_drawings[_specimen_id] = pd.DataFrame(group)

    specimen_id = 519482623
    drawings = layer_drawings[specimen_id]

    print(drawings)
    print(pia_wm_drawings[specimen_id])

    cld = CorticalLayerDrawings()
    for drawing in drawings.to_dict("records"):
        cld.register_layer_polygon(drawing["structure_acronym"], drawing["path"])

    new_shape = np.around([cld.xy_aspect_ratio * 600, 600]).astype(int)
    rescaled = cld.rescale(new_shape)

    distances = []
    for layer in rescaled.names:
        rasterized = rescaled.rasterize(new_shape, names=[layer])
        out, dist = skimage.morphology.medial_axis(1 - rasterized, return_distance=True)
        dist[np.where(rasterized)] = -np.inf
        distances.append(dist)

    fig, ax = plt.subplots()
    ax.imshow(rescaled.rasterize(new_shape))

    fig, ax = plt.subplots(1, len(distances))
    for ii, dist in enumerate(distances):
        ax[ii].imshow(dist)

    closest = np.argmin(distances, axis=0)
    fig, ax = plt.subplots()
    ax.imshow(closest)

    cvx = skimage.morphology.convex_hull_image(rescaled.rasterize(new_shape))
    closest_bound = closest.copy()
    closest_bound[~cvx] = -1 
    fig, ax = plt.subplots()
    ax.imshow(closest_bound)
    
    plt.show()
