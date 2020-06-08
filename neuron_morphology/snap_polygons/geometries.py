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
        self.close_bounds.update(*surface.bounds)

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
    translate = lambda ht, vt: (ht - box.horigin, vt - box.vorigin)
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
    return lambda horizontal, vertical: (horizontal * scale, vertical * scale)

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

    putative_polys = rasterio.features.shapes(closest.astype(np.uint16))
    # check for multiple polygons per label
    # pick largest if multiple exist
    polys, labels = zip(*putative_polys)
    labels_arr = np.array(labels)
    results_dict = {}
    for l in np.unique(labels_arr):
        if np.sum(labels_arr == l) > 1:
            biggest_poly_area = 0
            for ind in np.flatnonzero(labels_arr == l):
                cur_poly = Polygon(polys[ind]["coordinates"][0])
                if cur_poly.area > biggest_poly_area:
                    biggest_poly = cur_poly
                    biggest_poly_area = biggest_poly.area
            results_dict[name_lut[int(l)]] = biggest_poly
        else:
            ind = np.flatnonzero(labels_arr == l)[0]
            results_dict[name_lut[int(l)]] = Polygon(polys[ind]["coordinates"][0])

    return results_dict

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

    for ii, n in enumerate(names):
        current = polygons[n]
        # up side
        if ii == 0 and pia is not None:
            results[f"{n}_pia"] = pia
        else:
            above_layers = [polygons[name] for name in names[:ii]]
            results[f"{n}_pia"] = shared_faces(current, above_layers)

        # down side
        if ii == len(names) - 1 and wm is not None:
            results[f"{n}_wm"] = wm
        else:
            below_layers = [polygons[name] for name in names[ii + 1:]]
            results[f"{n}_wm"] = shared_faces(current, below_layers)

    return results

def shared_faces(poly, others):
    """ Given a polygon and a set of other polygons that could be adjacent on the same
    side, find and connect that shared face.

    Parameters
    ----------
    poly : Polygon
        Polygon whose boundary with others we want to identify
    others : list
        List of other Polygons

    Returns
    -------
    LineString representing the shared face
    """

    faces_list = []
    for o in others:
        geom_collection = shapely.ops.shared_paths(poly.exterior, o.exterior)
        if geom_collection.is_empty:
            continue
        _forward, backward = geom_collection
        faces = shapely.ops.linemerge(backward)
        if not faces.is_empty:
            faces_list.append(faces)

    merged_faces = shapely.ops.linemerge(faces_list)
    coordinates = list(merged_faces.coords)
    shared_line = ensure_linestring(coordinates)
    return shared_line
