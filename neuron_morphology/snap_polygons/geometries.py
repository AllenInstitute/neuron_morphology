from typing import Optional, Dict, Union, Sequence, Callable, Tuple, Iterable
import collections
import math
from functools import partial
import sys

import rasterio
import rasterio.features
import shapely.ops
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
import numpy as np
from scipy import ndimage

from neuron_morphology.snap_polygons.bounding_box import BoundingBox
from neuron_morphology.snap_polygons.types import (
    PolyType, LineType, TransformType, ensure_polygon, ensure_linestring,
    MultiPolygonResolverType
)


def select_largest_subpolygon(polygons, error_threshold):

    if isinstance(polygons, shapely.geometry.Polygon):
        return polygons
    
    polygons = [
        poly for poly in polygons 
        if poly.area > sys.float_info.epsilon
    ]

    if len(polygons) == 1:
        return polygons[0]
    elif len(polygons) == 0:
        raise ValueError("No argued geometries with nonzero area")

    largest = (-float("inf"), None)
    second = (-float("inf"), None)
    for subpolygon in polygons:
        area = subpolygon.area

        if area < sys.float_info.epsilon:
            continue

        if area > largest[0]:
            second = largest
            largest = (area, subpolygon)

    ratio = largest[0] / second[0]
    if ratio < error_threshold:
        raise ValueError(
            "no definitive largest polygon. "
            f"{largest[0]} / {second[0]} = {ratio} < {error_threshold}"
        )
    return largest[1]


class Geometries:

    default_multipolygon_resolver = partial(
        select_largest_subpolygon, 
        error_threshold=-float("inf")
    )

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

    def fill_gaps(
            self, 
            working_scale: float = 1.0, 
            multipolygon_resolver: Optional[MultiPolygonResolverType] = None
    ) -> "Geometries":
        """
        """
        multipolygon_resolver = multipolygon_resolver or self.default_multipolygon_resolver

        scale_to_working = make_scale(working_scale)
        working_geometries = self.transform(scale_to_working)

        raster_stack = working_geometries.rasterize()
        clear_overlaps(raster_stack)
        closest, closest_names = closest_from_stack(raster_stack)
        snapped_polygons = get_snapped_polys(closest, closest_names, multipolygon_resolver)

        result_geometries = Geometries()
        result_geometries.register_polygons(snapped_polygons)

        translation_from_working = make_translation(
            working_geometries.close_bounds.horigin, 
            working_geometries.close_bounds.vorigin
        )
        scale_from_working = make_scale(1.0 / working_scale)

        return (
            result_geometries
                .transform(translation_from_working)
                .transform(scale_from_working)
        )

    def cut(self, template: shapely.geometry.Polygon, multipolygon_resolver: Optional[MultiPolygonResolverType] = None) -> "Geometries":
        """
        """
        multipolygon_resolver = multipolygon_resolver or self.default_multipolygon_resolver
        result = Geometries()

        for key, polygon in self.polygons.items():
            polygon = polygon.intersection(template)
            polygon = multipolygon_resolver(polygon)
            result.register_polygon(key, polygon)

        for key, surface in self.surfaces.items():
            result.register_surface(key, surface.intersection(template))
    
        return result

    def convex_hull(self):
        hull = None
        for polygon in self.polygons.values():
            if hull is None:
                # why the intermediate hull-taking? Some layer polygons have 
                # loops at the corners. This breaks the union operation, since
                # they don't have a defined interior/exterior.
                hull = polygon.convex_hull
            else:
                hull = polygon.convex_hull.union(hull)
        return hull.convex_hull

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


def make_translation(horizontal, vertical):
    return lambda ht, vt: (ht + horizontal, vt + vertical)


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
    name_lut : Dict[int, str],
    multipolygon_resolver: MultiPolygonResolverType
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

    polygons = collections.defaultdict(list)
    for obtained, label in rasterio.features.shapes(closest.astype(np.uint16)):
        key = name_lut[label]
        for coords in obtained["coordinates"]:
            polygons[key].append(Polygon(coords))

    for key in list(polygons.keys()):
        polygons[key] = multipolygon_resolver(polygons[key])

    return polygons


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
