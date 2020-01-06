from typing import Optional, List

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.features.statistics.coordinates import CoordinateType

from neuron_morphology.feature_extractor.specializations import NODESET
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
    n = coordinates.shape[0]
    above = (coordinates[:, dimension] > maxv).sum() / n
    below = (coordinates[:, dimension] < minv).sum() / n
    overlap = 1 - above - below
    return above, overlap, below


def calculate_coordinate_overlap(coordinates_a,
                                 coordinates_b,
                                 dimension: int = 1):
    """
        Return the % of coordinates_a that are above, overlaping, and below
        coordinates_b, and the same for b over a

        Parameters
        ----------

        coordinates_a: 2d array-like with x, y, z cols

        coordinates_b: 2d array-like with x, y, z cols

        dimension: dimension to compare (0, 1, 2 for x, y, z), default 1 (y)

        Returns
        -------

        dict: a_above_b, a_overlap_b, a_below_b, or
              -1's if coordinates_b is empty
    """
    if not coordinates_b:
        a_above_b, a_overlap_b, a_below_b = (-1, -1, -1)

    else:
        coordinates_a = np.asarray(coordinates_a)
        coordinates_b = np.asarray(coordinates_b)

        min_b = coordinates_b[:, dimension].min()
        max_b = coordinates_b[:, dimension].max()

        a_above_b, a_overlap_b, a_below_b = \
            calculate_coordinate_overlap_from_min_max(
                coordinates_a, min_b, max_b)

    overlap_features = {}
    overlap_features['above'] = a_above_b
    overlap_features['overlap'] = a_overlap_b
    overlap_features['below'] = a_below_b

    return overlap_features


def calculate_overlap(morphology: Morphology,
                      node_set_a: NODESET,
                      node_set_b: NODESET,
                      coordinate_type: CoordinateType = CoordinateType.NODE,
                      dimension: int = 1):
    """
        Calculate % of coordinates of node_type_a that are above, overlapping,
        and between the coordinates of node_type_b for a particular morphology

        Parameters
        ----------
        morphology: Morphology Object

        node_set_a: one of the sets in NODESET
        node_set_b: one of the sets in NODESET
        coordinate_type: Restrict analysis to specific coordinate type
                         (see coordinates for options)
        dimension: dimension to compare (0, 1, 2 for x, y, z), default 1 (y)

    """
    if node_set_a == node_set_b:
        overlap_features = {'above': 0.0, 'overlap': 1.0, 'below': 0.0}
    else:
        coords_a = coordinate_type.get_coordinates(morphology, node_set_a)
        coords_b = coordinate_type.get_coordinates(morphology, node_set_b)

        overlap_features = calculate_coordinate_overlap(coords_a,
                                                        coords_b,
                                                        dimension=1)

    return overlap_features


def calculate_overlap_of_all_node_sets(
        morphology: Morphology,
        node_types: Optional[List[int]] = None,
        coordinate_type: CoordinateType = CoordinateType.NODE,
        dimension: int = 1):
    """
        Calculate % of coordinates of node_type_a that are above, overlapping,
        and between the coordinates of all of the node types for a particular
        morphology

        Parameters
        ----------
        morphology: Morphology Object
        node_types: list of node types to analyze
                    (see neuron_morphology.constants for types)
        coordinate_type: Restrict analysis to specific coordinate type
                         (see coordinates for options)
        dimension: dimension to compare (0, 1, 2 for x, y, z), default 1 (y)
    """

    coords_a = coordinate_type.get_coordinates(morphology,
                                               node_types=node_types)
    if not coords_a:
        raise ValueError(f'No nodes of type(s) {node_types} found')

    all_overlap_features: dict = {}
    for node_set in NODESET:

        # SKIP ALL, it will always be (0, 1, 0) for any node_types
        if node_set == NODESET.ALL:
            continue

        coords_b = coordinate_type.get_coordinates(morphology,
                                                   node_types=node_set.value)

        overlap_features = calculate_coordinate_overlap(
            coords_a, coords_b, dimension=dimension)

        # Append node type compared against to feature name
        for key in overlap_features.keys():
            new_key = key + '_' + node_set.name
            overlap_features[new_key] = overlap_features.pop(key)

        all_overlap_features.update(overlap_features)

    return all_overlap_features
