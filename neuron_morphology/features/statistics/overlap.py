from typing import Optional, List

import numpy as np

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import Geometric


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


@marked(Geometric)
def overlap(data: Data,
            node_types: Optional[List[int]] = None,
            node_types_to_compare: Optional[List[int]] = None,
            coord_type: COORD_TYPE = COORD_TYPE.NODE,
            dimension: int = 1):
    """
        Compares the locations of node_types to node_types_to_compare
        Calculate % of coordinates of node_types that are
        above, overlapping, and below the coordinates of node_types_to_compare

        Example: calculate_overlap(
                    morphology,
                    node_types=[AXON],
                    node_types_to_compare=[APICAL_DENDRITE, BASAL_DENDRITE])
                will return the percentage of AXON nodes that are above,
                overlapping, and below DENDRITE nodes

        Parameters
        ----------
        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)
        node_types_to_compare: a list of node types (see neuron_morphology constants)
        coord_type: Restrict analysis to specific coordinate type
            (see neuron_morphology.features.statistics.coordinates for options)
        dimension: dimension to compare (0, 1, 2 for x, y, z), default 1 (y)

    """
    coords_a = coord_type.get_coordinates(data.morphology, node_types)
    coords_b = coord_type.get_coordinates(data.morphology, node_types_to_compare)

    overlap_features = calculate_coordinate_overlap(coords_a,
                                                    coords_b,
                                                    dimension=1)
    return overlap_features
