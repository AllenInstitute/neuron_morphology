from __future__ import division
import numpy as np
from scipy.spatial.distance import euclidean
from shapely.geometry import Polygon, LineString
from operator import itemgetter


def transform_path_to_coordinates(path):

    """ Converts a list of comma-separated numbers to a list of coordinates """

    values = map(float, path.split(','))
    x = values[0::2]
    y = values[1::2]

    coordinates = zip(x, y)

    return coordinates


def find_linear_equation(point1, point2):

    """ Finds the linear equation for two points and returns the slope and b. The equation is y = (slope * x) + b """

    slope = (point1.y - point2.y)/(point1.x - point2.x)
    b = 0
    point1.y = (slope*point1.x) + b
    b = point1.y + (-slope)*point1.x

    return slope, b


def create

def calculate_shortest_distance(soma_coordinates, pia_coordinates, white_matter_coordinates):

    """ Calculates the shortest path between pia and white matter polygons
        that goes through the soma and is perpendicular to pia """

    "Find the point on Pia that is perpendicular to Soma"

    soma_point = Polygon(soma_coordinates).centroid
    pia_line = LineString(pia_coordinates)
    white_matter_line = LineString(white_matter_coordinates)
    projection_distance_from_soma = pia_line.project(soma_point)
    pia_point = pia_line.interpolate(projection_distance_from_soma)

    "Find two points outside the ranges of the pia and white matter coordinates"

    slope, b = find_linear_equation(soma_point, pia_point)

    first_point_x = max(pia_coordinates, key=itemgetter(0))[0] + 1000
    second_point_x = min(white_matter_coordinates, key=itemgetter(0))[0] - 1000
    first_point_y = (slope * first_point_x) + b
    second_point_y = (slope * second_point_x) + b

    print(first_point_x, first_point_y, second_point_x, second_point_y)

    "Create a line that goes through the points and soma and find the point of intersectsion with the white matter line"

    soma_line = LineString([(first_point_x, first_point_y), (pia_point.x, pia_point.y), (soma.x, soma.y)
                            , (second_point_x, second_point_y)])

    white_matter_point = soma_line.intersects(white_matter_line)
    print(white_matter_point)