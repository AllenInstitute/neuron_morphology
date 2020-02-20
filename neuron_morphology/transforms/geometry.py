""" Some handy utilities for working with vector geometries
"""

from typing import List, Tuple, Callable

from shapely import geometry as geo


def get_ccw_vertices_from_two_lines(line1: List[Tuple], line2: List[Tuple]):
    """
        Convenience method two do both get_vertices_from_two_lines()
        and get_ccw_vertices()
    """
    return get_ccw_vertices(get_vertices_from_two_lines(line1, line2))

def get_vertices_from_two_lines(line1: List[Tuple], line2: List[Tuple]):
    """
        Generates circular vertices from two lines

        Parameters
        ----------
        line1, line2: List of coordinates describing two lines

        Returns
        -------
        vertices of the simple polygon created from line 1 and 2
        (first vertex = last vertex)

        1-2-3-4
        5-6-7-8 -> [1-2-3-4-8-7-6-5-1]

    """
    side1 = geo.LineString([line1[0], line2[-1]])
    side2 = geo.LineString([line1[-1], line2[0]])

    if side1.crosses(side2):
        line2.reverse()

    vertices = line1 + line2 + [line1[0]]
    return vertices

def get_ccw_vertices(vertices: List[Tuple]):
    """
        Generates counter clockwise vertices from vertices describing
        a simple polygon

        Method: Simplification of the shoelace formula, which calculates
        area of a simple polygon by integrating the area under each line
        segment of the polygon. If the total area is positive, the vertices
        were traversed in clockwise order, and if it is negative, they were
        traversed in counterclockwise order.

        Parameters
        ----------
        vertices: vertices describing a convex polygon
                  (vertices[0] = vertices[-1])

        Returns
        -------
        vertices in counter clockwise order

    """

    winding = 0
    for i in range(len(vertices)-1):
        (x0, y0) = vertices[i]
        (x1, y1) = vertices[i+1]
        winding += (x1 - x0) * (y1 + y0)

    if winding > 0:
        vertices.reverse()

    return vertices