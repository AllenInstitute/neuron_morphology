from typing import Callable

import numpy as np

from neuron_morphology.snap_polygons.types import TransformType


class BoundingBox:

    __slots__ = ["vorigin", "horigin", "vextent", "hextent"]

    # one might think these should be int, but we want to be able to record 
    # precisely the actual bounding box of some polygons with float vertices 
    # (then scale and convert to int at a requested resolution when necessary)
    def __init__(
        self, 
        horigin: float, 
        vorigin: float, 
        hextent: float,
        vextent: float, 
    ):
        """ Represents the bounds of a set of 2D objects

        Parameters
        ----------
        vorigin, horigin : the near corner of the box
        vextent, hextent : the far corner of the box

        """

        self.vorigin = vorigin
        self.horigin = horigin

        self.vextent = vextent
        self.hextent = hextent


    def __repr__(self):
        return (
            f"BoundingBox({self.horigin}, {self.vorigin}, "
            f"{self.hextent}, {self.vextent})"
        )

    @property
    def width(self) -> float:
        return self.hextent - self.horigin

    @property
    def height(self) -> float:
        return self.vextent - self.vorigin

    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height 
    
    @property
    def origin(self):
        return [self.horigin, self.vorigin]

    @property
    def extent(self):
        return [self.hextent, self.vextent]

    @property
    def coordinates(self):
        return [self.horigin, self.vorigin, self.hextent, self.vextent]

    def update(
        self, 
        horigin: float, 
        vorigin: float, 
        hextent: float,
        vextent: float, 
    ):
        """ Potentially enlarges this box.

        Parameters
        ----------
        As to the constructor of BoundingBox. The new shape of this box is the 
            smallest box enclosing both this and the inputs.

        """

        self.vorigin = min(self.vorigin, vorigin)
        self.horigin = min(self.horigin, horigin)

        self.vextent = max(self.vextent, vextent)
        self.hextent = max(self.hextent, hextent)


    def transform(
        self, 
        transform: TransformType, 
        inplace: bool = False
    ) -> "BoundingBox":
        """ Apply a transform to this box

        Parameters
        ----------
        transform : A callable which maps (vertical, horizontal) coordinates to 
            new (vertical, horizontal) coordinates.
        inplace : if True, apply the transform to this object

        Returns
        -------
        The transformed box (potentially self)

        """

        if inplace:
            obj = self
        else:
            obj = self.copy()

        obj.horigin, obj.vorigin = transform(
            obj.horigin, obj.vorigin)
        obj.hextent, obj.vextent = transform(
            obj.hextent, obj.vextent)
        
        return obj

    def copy(self) -> "BoundingBox":
        """ Duplicates this bounding box

        Returns
        -------
        A copy of this object.

        """

        return self.__class__(
            self.horigin, self.vorigin, 
            self.hextent, self.vextent
        )

    def round(
        self, 
        inplace: bool = False, 
        origin_via: Callable[[float], float] = np.around,
        extent_via: Callable[[float], float] = np.around,
    ):
        """ Round the coordinates of this box

        Parameters
        ----------
        inplace : If True, round the coordinates of this object
        origin_via : method to use when rounding the origin
        extent_via : method to use when rounding the extent

        Returns
        -------
        The rounded box (potentially self.

        """

        if inplace:
            obj = self
        else:
            obj = self.copy()

        obj.vorigin = origin_via(obj.vorigin)
        obj.horigin = origin_via(obj.horigin)

        obj.vextent = extent_via(obj.vextent)
        obj.hextent = extent_via(obj.hextent)

        return obj
