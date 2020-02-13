from typing import Optional, Dict, Union, Sequence, Callable, Tuple
import collections
import math

import rasterio
import rasterio.features
import shapely.ops
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
import numpy as np
from scipy import ndimage

from neuron_morphology.snap_polygons.bounding_box import BoundingBox
from neuron_morphology.snap_polygons.types import (
    PolyType, LineType, TransformType, ensure_polygon, ensure_linestring
)

class Geometries:

    def __init__(self):
        """ A collection of polygons and lines
        """

        self._close_bounds: Optional[BoundingBox] = None

        self.polygons: Dict[str, Polygon] = {}
        self.surfaces: Dict[str, LineString] = {}

    @property
    def close_bounds(self):
        if self._close_bounds is None:
            self._close_bounds = BoundingBox(
                np.inf, np.inf, -np.inf, -np.inf
            )
        return self._close_bounds

    @close_bounds.setter
    def close_bounds(self, value: BoundingBox):
        self._close_bounds = value

    def register_polygon(
        self, 
        name: str, 
        path: PolyType
    ):
        """ Adds a named polygon path to this object. Updates the close 
        bounding box.

        Parameters
        ----------
        name : identifier for this polygon
        path : defines the exterior of this (simple) polygon


        """

        polygon = ensure_polygon(path)
        # ho, vo, he, ve = polygon.bounds
        # self.close_bounds.update(vo, ho, ve, he)
        self.close_bounds.update(*polygon.bounds)

        self.polygons[name] = polygon


    def _register_many(
        self, 
        objects: Union[
            Dict[str, Union[LineType, PolyType]],
            Sequence[Dict[str, Union[LineType, PolyType]]]
        ], 
        method: Callable[[str, Union[LineType, PolyType]], None]
    ):
        """ Utility for registering many polygons or surfaces. See 
        register_polygons and register_surfaces for use.
        """

        if isinstance(objects, collections.Sequence):
            for obj in objects:
                method(obj["name"], obj["path"])

        elif isinstance(objects, collections.Mapping):
            for name, path in objects.items():
                method(name, path)

        else:
            raise TypeError(f"did not understand type: {type(objects)}")

    def register_polygons(
        self, 
        polygons: Union[
            Dict[str, PolyType],
            Sequence[Dict[str, PolyType]]
        ]
    ):
        """ utility for registering multiple polygons. See register_polygon
        """
        self._register_many(polygons, self.register_polygon)

    def register_surface(
        self, 
        name: str, 
        path: LineType
    ):
        """ Adds a line (e.g. the pia/wm surfaces) to this object. Updates 
        the bounding box.

        Parameters
        ----------
        name : identifier for this surface
        path : defines the surface

        """

        surface = ensure_linestring(path)
        ho, vo, he, ve = surface.bounds
        self.close_bounds.update(vo, ho, ve, he)

        self.surfaces[name] = surface


    def register_surfaces(self, surfaces: Dict[str, LineType]):
        """ utility for registering multiple surfaces. See register_surface
        """
        self._register_many(surfaces, self.register_surface)


    def rasterize(
        self, 
        box: Optional[BoundingBox] = None,
        polygons: Union[Sequence[str], bool] = True, 
        surfaces: Union[Sequence[str], bool] = False
    ) -> Dict[str, np.ndarray]:
        """ Rasterize one or more owned geometries. Produce a mapping from object names to masks.

        Parameters
        ----------
        shape : if provided, the output image shape. Otherwise, use     the rounded close bounding box shape
        polygons : a list of names. Alternatively all (True) or none    (False)
        lines : a list of names. Alternatively all (True) or none       (False)

        Notes
        -----
        uses rasterio.features.rasterize

        """

        if box is None:
            box = self.close_bounds
        
        if polygons is True:
            polygons = list(self.polygons.keys())
        elif polygons is False:
            polygons = []
        
        if surfaces is True:
            surfaces = list(self.surfaces.keys())
        elif surfaces is False:
            surfaces = []

        stack = {}

        for name in polygons:
            stack[name] = rasterize(self.polygons[name], box)
        
        for name in surfaces:
            stack[name] = rasterize(self.surfaces[name], box)

        return stack
        

    def transform(
        self, 
        transform: TransformType
    ) -> "Geometries":
        """ Apply a transform to each owned geometry. Return a new collection.

        Parameters
        ----------
        transform : A callable which maps (vertical, horizontal) coordinates to 
            new (vertical, horizontal) coordinates.

        """

        out = Geometries()

        for name, poly in self.polygons.items():
            out.register_polygon(name, shapely.ops.transform(transform, poly))

        for name, surf in self.surfaces.items():
            out.register_surface(name, shapely.ops.transform(transform, surf))

        return out

    def to_json(self) -> Dict:
        """ Write contained polygons to a json-serializable format
        """

        return {
            "polygons": [
                {
                    "name": name,
                    "path": np.array(poly.exterior.coords).tolist()
                }
                for name, poly in self.polygons.items()
            ],
            "surfaces": [
                {
                    "name": name,
                    "path": np.array(surf.coords).tolist()
                }
                for name, surf in self.surfaces.items()
            ]
        }

def rasterize(
    geometry: shapely.geometry.base.BaseGeometry, 
    box: BoundingBox
) -> np.array:
    """ Rasterize a shapely object to a grid defined by a provided bounding box.

    Parameters
    ----------
    geometry : to be rasterized
    box : defines the window (in the same coordinate space as the geometry) 
        into which the geometry will be rasterized

    Returns
    -------
    A mask, where 1 indicates presence and 0 absence

    """

    box = box.round(origin_via=math.floor, extent_via=math.ceil)
    translate = lambda v, h: (v - box.vorigin, h - box.horigin)
    geometry = shapely.ops.transform(translate, geometry)
    out_shape = (box.height, box.width)

    return rasterio.features.rasterize(
        [(geometry, 1)],
        out_shape=out_shape
    )


def make_scale(
    scale: float = 1.0
) -> Callable[[float, float], Tuple[float, float]]:
    """ A utility for making a 2D scale transform, suitable for transforming
    bounding boxes and Geometries

    Parameters
    ----------
    scale : isometric scale factor

    Returns
    -------
    A transform function

    """
    return lambda vertical, horizontal: (vertical * scale, horizontal * scale)

def clear_overlaps(stack: Dict[str, np.ndarray]):
    """ Given a stack of masks, remove all inter-mask overlaps inplace

    Parameters
    ----------
    stack : Keys are names, values are masks (of the same shape). 0 indicates
        absence

    """

    overlaps = np.array(list(stack.values())).sum(axis=0) >= 2

    for image in stack.values():
        image[overlaps] = 0

def closest_from_stack(stack: Dict[str, np.ndarray]):
    """ Given a stack of images describing distance from several objects, find 
    the closest object to each pixel.

    Parameters
    ----------
    stack : Keys are names, values are ndarrays (of the same shape). Each pixel 
        in the values describes the distance from that pixel to the named object
    
    Returns
    -------
    closest : An integer array whose values are the closest object to each 
        pixel
    names : A mapping from the integer codes in the "closest" array to names

    """

    distances = []
    names = {}

    for ii, (name, mask) in enumerate(stack.items()):
        distances.append(ndimage.distance_transform_edt(1 - mask))
        names[ii + 1] = name

    closest = np.squeeze(np.argmin(distances, axis=0)) + 1
    return closest, names

def get_snapped_polys(
    closest: np.ndarray, 
    name_lut : Dict[int, str]
) -> Dict[str, Polygon]:
    """ Obtains named shapes from a label image.

    Parameters
    ----------
    closest : label integer with integer codes
    name_lut : look up table from integer codes to string names

    Returns
    -------
    mapping from names to polygons describing each labelled region

    """

    return {
        name_lut[int(label)]:
            Polygon(poly["coordinates"][0])
        for poly, label
        in rasterio.features.shapes(closest.astype(np.uint16))
        if int(label) in name_lut
    }

def find_vertical_surfaces(
    polygons: Dict[str, Polygon], 
    order: Sequence[str], 
    pia: Optional[LineString] = None, 
    wm: Optional[LineString] = None
):
    """ Given a set of polygons describing cortical layer boundaries, find the 
    boundaries between each layer.

    Parameters
    ----------
    polygons : named layer polygons
    order : A sequence of names defining the order of the layer polygons from 
        pia to white matter
    pia : The upper pia surface. 
    wm : The lower white matter surface.

    Returns
    -------
    dictionary whose keys are as "{name}_{side}" and whose values are 
        linestrings describing these boundaries. 

    """

    names = [name for name in order if name in polygons]
    results = {}

    for ii, (up_name, down_name) in enumerate(zip(names[:-1], names[1:])):

        up = polygons[up_name]
        down = polygons[down_name]

        _same, diff = shapely.ops.shared_paths(up.exterior, down.exterior)
        faces = shapely.ops.linemerge(diff)
        coordinates = list(faces.coords)
        shared_line = ensure_linestring(coordinates)

        if ii == 0 and pia is not None:
            results[f"{up_name}_pia"] = pia
        if ii == len(names) - 2 and wm is not None:
            results[f"{down_name}_wm"] = wm
        
        results[f"{up_name}_wm"] = shared_line
        results[f"{down_name}_pia"] = shared_line

    return results
