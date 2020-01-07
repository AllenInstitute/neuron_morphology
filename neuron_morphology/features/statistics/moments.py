from typing import Optional, List

import numpy as np
from scipy import stats

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE


def moments(data: Data,
            node_types: Optional[List] = None,
            coord_type: COORD_TYPE = COORD_TYPE.NODE,
            ):
    """
        Calculate the moments of specific coordinate type and node type

        Parameters
        ----------
        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)
        coord_type: Restrict analysis to specific coordinate type
            (see neuron_morphology.features.statistics.coordinates for options)
    """

    coordinates = coord_type.get_coordinates(
                    data.morphology, node_types=node_types)
    if not coordinates:
        moment_features = {
            'mean': float('nan'),
            'std': float('nan'),
            'var': float('nan'),
            'skew': float('nan'),
            'kurt': float('nan')}

    else:
        coordinates = np.asarray(coordinates)
        (_, _, mean, variance, skew, kurt) = stats.describe(coordinates, axis=0)
        std = np.sqrt(variance)

        moment_features = {
            'mean': mean,
            'std': std,
            'var': variance,
            'skew': skew,
            'kurt': kurt}

    return moment_features
