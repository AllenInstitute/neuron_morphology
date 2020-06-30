from typing import Union, Sequence, List, Dict, Callable, Tuple, Iterable
import collections

import numpy as np
from shapely.geometry.polygon import Polygon, LinearRing
from shapely.geometry import LineString


NicePathType = Sequence[Sequence[float]] # [[x, y], [x, y]]

PathType = Union[
    str, # "x,y,x,y"
    NicePathType
]

PathsType = Dict[str, PathType]

PolyType = Union[
    PathType,
    Polygon, 
    LinearRing
]

LineType = Union[
    PathType,
    LineString
]

TransformType = Callable[
    [float, float],
    Tuple[float, float]
]

MultiPolygonResolverType = Callable[[Iterable[Polygon]], Polygon]
MultiSurfaceResolvertype = Callable[[Iterable[LineString]], LineString]

def ensure_polygon(candidate: PolyType) -> Polygon:
    """ Convert from one of many polygon representations to Polygon
    """
    candidate = ensure_path(candidate)

    if isinstance(candidate, Polygon):
        return candidate
    elif isinstance(candidate, LinearRing):
        return Polygon(candidate)
    elif isinstance(candidate, collections.Sequence):
        return Polygon([item for item in map(tuple, candidate)])
    else:
        raise TypeError(f"did not understand type: {type(candidate)}")


def ensure_linestring(candidate: LineType) -> LineString:
    """ Convert from one of many line representations to LineString
    """

    candidate = ensure_path(candidate)
    if isinstance(candidate, LineString):
        return candidate
    elif isinstance(candidate, collections.Sequence):
        return LineString(list(map(tuple, candidate)))
    else:
        raise TypeError(f"did not understand type: {type(candidate)}")


def ensure_path(
    candidate: PathType, 
    num_dims: int = 2
) -> NicePathType:
    """ Ensure that an input path, which might be a "x,y,x,y" string, is 
    represented as a list of lists instead.

    Parameters
    ----------
    candidate : input coordinate sequence
    num_dims : how manu elements define a coordinate

    Returns
    -------
    Contents of inputs, with each coordinate a list of float

    """

    if isinstance(candidate, str):
        return split_pathstring(candidate, num_dims=num_dims)
    return candidate


def split_pathstring(
    pathstring: str, 
    num_dims: int = 2, 
    sep: str = ","
) -> NicePathType:
    """ Converts a pathstring ("x,y,x,y...") to a num_points X num_dims 
    list of lists of float

    Parameters
    ----------
    pathstring : input coordinate sequence
    num_dims : how manu elements define a coordinate
    sep : character separating elements

    Returns
    -------
    Contents of pathstring, with each coordinate a list of float

    """
    
    split = list(map(float, pathstring.split(sep)))
    divisions = len(split) / num_dims
    floor_divisions = int(divisions)
    
    if divisions - floor_divisions:
        raise ValueError(
            f"unable to split {len(split)} long path among "
            f"{num_dims} dimensions"
        )
    
    return np.reshape(split, (floor_divisions, num_dims)).tolist()
