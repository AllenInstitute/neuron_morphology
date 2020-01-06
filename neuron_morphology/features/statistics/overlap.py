from typing import Optional

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.features.statistics.coordinates import CoordinateType

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    Geometric,
    BifurcationFeatures,
    CompartmentFeatures)


def calculate_coordinate_overlap_from_min_max(coordinates: np.ndarray,
                                              minv: float,
                                              maxv: float,
                                              dimension: int = 1):
    """
        Return the % of coordinates that are above the max,
        between, or below the min

        Parameters
        ----------

        coordinates: np.ndarray with x, y, z columns

        minv: min to check against

        maxv: max to check against

        dimension: dimension to compare (0, 1, 2 for x, y, z), default 1 (y)

    """
    n = coordinates.shape()[0]
    above = (coordinates[:, dimension] > maxv).sum() / n
    below = (coordinates[:, dimension] < minv).sum() / n
    overlap = 1 - above - below
    return above, overlap, below


def calculate_coordinate_overlap(coordinates_a, coordinates_b,
                                 name_a: str = 'a',
                                 name_b: str = 'b',
                                 dimension: int = 1):
    """
        Return the % of coordinates_a that are above, overlaping, and below
        coordinates_b, and the same for b over a

        Parameters
        ----------

        coordinates_a: 2d array-like with x, y, z cols
        coordinates_b: 2d array-like with x, y, z cols
        name_a: str name to use in output dictionary
        name_b: str name to use in output dictionary
        dimension: int (0, 1, 2)

        Returns
        -------

        dict: a_above_b, a_overlap_b, a_below_b,
    """
    coordinates_a = np.asarray(coordinates_a)
    coordinates_b = np.asarray(coordinates_b)

    min_b = coordinates_b[:, dimension].min()
    max_b = coordinates_b[:, dimension].max()

    a_above_b, a_overlap_b, a_below_b = \
        calculate_coordinate_overlap_from_min_max(coordinates_a, min_b, max_b)

    overlap_features = {}
    overlap_features[name_a + '_above_' + name_b] = a_above_b
    overlap_features[name_a + '_overlap_' + name_b] = a_overlap_b
    overlap_features[name_a + '_below_' + name_b] = a_below_b

    return overlap_features


def calculate_overlap(morphology,
                      node_type_a,
                      node_type_b,
                      coordinate_type: CoordinateType = CoordinateType.NODE,
                      dimension: int = 1):
    """
        Calculate % of coordinates of node_type_a that are above, overlapping,
        and between the coordinates of node_type_b for a particular morphology

        Parameters
        ----------
        morphology: Morphology Object
    """

    coords_a = coordinate_type.get_coordinates(morphology, node_type_a)
    coords_b = coordinate_type.get_coordinates(morphology, node_type_b)

    overlap_features = calculate_coordinate_overlap(coords_a,
                                                    coords_b,
                                                    name_a='',
                                                    name_b='',
                                                    dimension=1)

    return overlap_features
