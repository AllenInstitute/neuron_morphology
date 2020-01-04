from typing import Optional

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.features.statistics import coordinates
from neuron_morphology.constants import AXON, BASAL_DENDRITE, APICAL_DENDRITE


from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    Geometric,
    BifurcationFeatures,
    CompartmentFeatures)


def get_sort_min_max(coordinates, dimension: int = 1):
    """
        Sort a list of coordinates by dimension and return max and min values

        Parameters
        ----------

        coordinates: 2d array-like with x, y, z, cols

        Returns
        -------
        sorted_coords: coordinates sorted by dimension
        max: maximum value of dimension
        min: minimum value of dimension
    """
    coordinates = np.asarray(coordinates)
    sorted_coords = coordinates[coordinates[:, dimension].argsort()]
    return (sorted_coords,
            sorted_coords[:, dimension].max(),
            sorted_coords[:, dimension].min())


def calculate_coordinate_overlap_from_min_max(coordinates, minv, maxv,
                                              dimension: int = 1):
    """
        Return the % of coordinates that are above the max,
        between, or below the min
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
              b_above_a, b_overlap_a, b_below_a


    """
    sorted_a, min_a, max_a = get_sort_min_max(coordinates_a)
    sorted_b, min_b, max_b = get_sort_min_max(coordinates_b)

    a_above_b, a_overlap_b, a_below_b = \
        calculate_coordinate_overlap_from_min_max(sorted_a, min_b, max_b)

    b_above_a, b_overlap_a, b_below_a = \
        calculate_coordinate_overlap_from_min_max(sorted_b, min_a, max_a)

    overlap_features = {}
    overlap_features[name_a + '_above_' + name_b] = a_above_b
    overlap_features[name_a + '_overlap_' + name_b] = a_overlap_b
    overlap_features[name_a + '_below_' + name_b] = a_below_b
    overlap_features[name_b + '_above_' + name_a] = b_above_a
    overlap_features[name_b + '_overlap_' + name_a] = b_overlap_a
    overlap_features[name_b + '_below_' + name_a] = b_below_a

    return overlap_features


def calculate_overlap(morphology,
                      node_type_a,
                      node_type_b,
                      special_type: int = NODES,
                      dimension: int = 1):
    """
        Calculate % of coordinates of node_type_a that are above, overlapping,
        and between the coordinates of node_type_b for a particular morphology

        Parameters
        ----------
        morphology: Morphology Object
    """

    type_a_nodes = morphology.get_nodes_by_type(node_types=[node_type_a])
    type_b_nodes = morphology.get_nodes_by_type(node_types=[node_type_b])

    if not type_a_nodes:
        raise ValueError(f'No nodes found of type {node_type_a},'
                         f' unable to compare {node_type_a} to {node_type_b}')
    if not type_b_nodes:
        raise ValueError(f'No nodes found of type {node_type_b},'
                         f' unable to compare {node_type_a} to {node_type_b}')

    coords_b_dim = [node[dimension] for node in type_b_nodes]
    b_max = max(coords_b_dim)
    b_min = min(coords_b_dim)



