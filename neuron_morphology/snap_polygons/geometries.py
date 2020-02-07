from typing import Optional, Dict, Union, Sequence, Tuple
import collections

import rasterio
import rasterio.features
import shapely.ops
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
import numpy as np

from neuron_morphology.snap_polygons.bounding_box import BoundingBox
from neuron_morphology.snap_polygons.types import (
    PolyType, LineType, TransformType, ensure_polygon, ensure_linestring
)

class Geometries:

    def __init__(
        self, 
        original_bounds: BoundingBox
    ):
        """ A collection of polygons and lines
        """

        self.original_bounds: BoundingBox = original_bounds
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
        """ Adds a layer polygon path to this object. Updates the close bounding box.
        """

        polygon = ensure_polygon(path)
        self.close_bounds.update(*polygon.bounds)

        self.polygons[name] = polygon


    def register_polygons(
        self, 
        polygons: Union[
            Dict[str, PolyType],
            Sequence[Dict[str, Union[str, PolyType]]]
        ]
    ):
        """ utility for registering multiple polygons
        """

        if isinstance(polygons, collections.Sequence):
            for poly in polygons:
                self.register_polygon(poly["name"], poly["path"])

        elif isinstance(polygons, collections.Mapping):
            for name, path in polygons.items():
                self.register_polygon(name, path)
        else:
            raise TypeError(f"did not understand type: {type(polygons)}")

    def register_surface(
        self, 
        name: str, 
        path: LineType
    ):
        """ Adds a line (e.g. the pia/wm surfaces) to this object. Updates the bounding box.
        """

        surface = ensure_linestring(path)
        self.close_bounds.update(*surface.bounds)

        self.surfaces[name] = surface


    def register_surfaces(self, surfaces: Dict[str, LineType]):
        """ utility for registering multiple surfaces
        """
        raise NotImplementedError

    def rasterize(
        self, 
        shape: Optional[Tuple[int, int]] = None,
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

        if shape is None:
            shape = (
                int(np.around(self.close_bounds.height)),
                int(np.around(self.close_bounds.width))
            )
        
        if polygons is True:
            polygons = self.polygons.keys()
        elif polygons is False:
            polygons = []
        
        if surfaces is True:
            surfaces = self.surfaces.keys()
        elif surfaces is False:
            surfaces = []

        stack = {}

        for name in polygons:
            stack[name] = rasterize(self.polygons[name], self.close_bounds)
        
        for name in surfaces:
            stack[name] = rasterize(self.surfaces[name], self.close_bounds)

        return stack
        

    def transform(
        self, 
        transform: TransformType
    ) -> "Geometries":
        """ Apply a transform to each owned geometry. Return a new collection.
        """

        out = Geometries(self.original_bounds.transform(transform))

        for name, poly in self.polygons.items():
            out.register_polygon(name, shapely.ops.transform(transform, poly))

        for name, surf in self.surfaces.items():
            out.register_surface(name, shapely.ops.transform(transform, surf))

        return out

    def to_json(self) -> Dict:
        """ Write contained polygons to a json-serializable format
        """

    def overlay(self, image: np.ndarray) -> np.ndarray:
        """ Burn this object's geometries onto a provided image as 
        colored transparent objects.
        """

def rasterize(
    geometry: shapely.geometry.base.BaseGeometry, 
    box: BoundingBox
) -> np.array:

    box = box.round()
    translate = lambda v, h: (v - box.vert_origin, h - box.hor_origin)
    geometry = shapely.ops.transform(translate, geometry)
    out_shape = (box.height, box.width)

    return rasterio.features.rasterize(
        [(geometry, 1)],
        out_shape=out_shape
    )