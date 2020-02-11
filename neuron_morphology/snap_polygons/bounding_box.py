from typing import NamedTuple, Callable

import numpy as np

from neuron_morphology.snap_polygons.types import TransformType


class BoundingBox:
    """
    """

    

    __slots__ = ["vert_origin", "hor_origin", "vert_extent", "hor_extent"]

    # one might think these should be int, but we want to be able to record 
    # precisely the actual bounding box of some polygons with float vertices 
    # (then scale and convert to int at a requested resolution when necessary)
    def __init__(
        self, 
        vert_origin: float, 
        hor_origin: float, 
        vert_extent: float, 
        hor_extent: float
    ):

        # near corner
        self.vert_origin = vert_origin
        self.hor_origin = hor_origin

        # far corner
        self.vert_extent = vert_extent
        self.hor_extent = hor_extent


    def __repr__(self):
        return (
            f"BoundingBox({self.vert_origin}, {self.hor_origin}, "
            f"{self.vert_extent}, {self.hor_extent})"
        )

    @property
    def width(self) -> float:
        return self.hor_extent - self.hor_origin

    @property
    def height(self) -> float:
        return self.vert_extent - self.vert_origin

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height 

    def update(
        self, 
        vert_origin: float, 
        hor_origin: float, 
        vert_extent: float, 
        hor_extent: float
    ):
        """ Potentially enlarges this box.
        """

        self.vert_origin = min(self.vert_origin, vert_origin)
        self.hor_origin = min(self.hor_origin, hor_origin)

        self.vert_extent = max(self.vert_extent, vert_extent)
        self.hor_extent = max(self.hor_extent, hor_extent)


    def transform(
        self, 
        transform: TransformType, 
        inplace: bool = False
    ) -> "BoundingBox":
        """ Apply a transform to this box
        """

        if inplace:
            obj = self
        else:
            obj = self.copy()

        obj.vert_origin, obj.hor_origin = transform(
            obj.vert_origin, obj.hor_origin)
        obj.vert_extent, obj.hor_extent = transform(
            obj.vert_extent, obj.hor_extent)
        
        return obj

    def copy(self) -> "BoundingBox":
        return self.__class__(
            self.vert_origin, self.hor_origin, 
            self.vert_extent, self.hor_extent
        )

    def round(self, inplace: bool = False, via=np.around):

        if inplace:
            obj = self
        else:
            obj = self.copy()

        for name in obj.__slots__:
            setattr(
                obj, 
                name, 
                int(via(getattr(obj, name)))
            )

        return obj