""" This module contains utilities for processing cortical surface drawings. 
In general we take these as given (they even take precedence of e.g. the 
upper and lower surfaces of layers 1 and 6b for instance), but some drawings 
pose resolvable problems.

The main such problem occurs when cortical layer drawings extend far from the 
layer drawings. Extrapolating layer drawings into this space is dangerous and 
not very useful (only the drawings near the cell are useful downstream). The 
solution implemented here is to cut out a segment of each surface whose 
endpoints are sufficiently close to the layer drawings and discard the rest.
"""
from typing import Union, Tuple, Callable, Sequence
import copy as cp
import logging

from shapely.geometry import LineString, Point
from shapely.geometry.base import BaseGeometry

from neuron_morphology.snap_polygons.types import LineType, ensure_linestring


ConditionFn = Callable[[Point], bool]


def trim_to_close(
        geometry: BaseGeometry, 
        threshold: float, 
        linestring: LineType,
        iterations: int = 10
) -> LineString:
    """Find the longest segment of a linestring whose endpoints are within a 
    specified distance of a geometry.

    Parameters
    ----------
    geometry : Acceptable distances are defined as extending from this object.
    threshold : Acceptable distances are less than or equal to this value
    linestring : to be trimmed (not in place)
    iterations : Use this many iterations to refine the endpoints of the 
        linestring

    Returns
    -------
    a trimmed copy of the input linestring

    """

    linestring = ensure_linestring(cp.deepcopy(linestring))

    def condition(point: Point) -> bool:
        return geometry.distance(Point(point)) <= threshold

    try:
        coords = trim_coords(
            linestring.coords, 
            condition=condition,
            iterations=iterations,
        )
    except ValueError:
        logging.error("no point within %s of argued geometry", threshold)
        raise

    return LineString(coords)


def find_transition(
        unmet: Point, 
        met: Point, 
        condition: ConditionFn, 
        iterations: int
) -> Point:
    """Given two points in space, one of which meets a condition, locate the 
    position along a line segment between these points where the condition 
    becomes true.

    Parameters
    ----------
    unmet : a point at which the condition is not met
    met : a point at which the condition is met
    condition : used to evaluate intermediate points
    iterations : refine this many times 

    Returns
    -------
    A point along the input segment at which the condition is met.

    Notes
    -----
    No such transition point is required to exist. In that case, this function 
    will find an arbitrary condition-meeting point along the segment. For our 
    use case, this misbehavior is tolerable because an exact transition point 
    is not required.
    """

    segment = LineString([unmet, met])
    midpoint = segment.interpolate(segment.length / 2)

    if condition(midpoint):
        met = midpoint
    else:
        unmet = midpoint

    if iterations > 0:
        return find_transition(unmet, met, condition, iterations - 1)
    return met
   

def first_met(
        coords: Sequence[Union[Point, Tuple]], 
        condition: ConditionFn, 
        iterations: int
) -> Tuple[int, Point]:
    """Locate the first point along a coordinate sequence at which a condition 
    is met.

    Parameters
    ----------
    coords : sequence to evaluate
    condition : used to evaluate points
    iterations : how many times to refine the transition point.

    Returns
    -------
    The index and value of the transition point.
    """
    
    for idx, coord in enumerate(coords):
        coord = Point(coord)
        met = condition(coord)

        if met:
            if idx == 0:
                return idx, coord
            return idx, find_transition(
                coords[idx - 1], coord, condition, iterations
            )

    raise ValueError("condition never met!")


def remove_duplicates(coords: Sequence[Point]) -> Sequence[Point]:
    """Remove duplicate points from a coordinate sequence.

    Parameters
    ----------
    coords : sequence with potential duplicates

    Returns
    -------
    list of coordinates with duplicates removed
    """
    if len(coords) < 2:
        return coords

    out = [coords[0]]
    for coord in coords[1:]:
        coord = Point(coord)
        if coord != out[-1]:
            out.append(coord)

    return out


def trim_coords(
        coords: Sequence[Union[Point, Tuple]], 
        condition: ConditionFn, 
        iterations: int
):  
    """Find the longest subinterval of a coordinate sequence whose endpoints 
    meet some condition.

    Parameters
    ----------
    coords : sequence to trim
    condition : used to evaluate points
    iterations : how many times to refine the endpoints.

    Returns
    -------
    Trimmed sequence
    """

    left_index, left_pt = first_met(coords, condition, iterations)
    right_index, right_pt = first_met(coords[::-1], condition, iterations)

    if right_index > 0:
        coords = list(coords[:-right_index]) + [right_pt]
    if left_index > 0:
        coords = [left_pt] + list(coords[left_index:])

    return remove_duplicates(coords)
