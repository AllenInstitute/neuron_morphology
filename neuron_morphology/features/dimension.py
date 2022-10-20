from typing import Optional, List

import numpy as np

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    Geometric,
    RequiresRoot
    )

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE


@marked(RequiresRoot)
@marked(Geometric)
def dimension(
            data: Data,
            node_types: Optional[List] = None,
            coord_type: COORD_TYPE = COORD_TYPE.NODE,
            signed_bias = (False, True, False),
            ):
    """
        Get the height, width, depth, minimum, and maximum values of
        specific coordinate type and node type centered about the root

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

        coord_type: Restrict analysis to specific coordinate type
            (see neuron_morphology.features.statistics.coordinates for options)

        signed_bias: boolean tuple for whether the bias measure should be signed
             for (x, y, z)

    """
    coordinates = coord_type.get_coordinates(
                    data.morphology, node_types=node_types)
    if not coordinates:
        nan_array = np.empty((3,))
        nan_array[:] = np.nan

        dimension_features = {
            'height': float('nan'),
            'width': float('nan'),
            'depth': float('nan'),
            'min_xyz': nan_array,
            'max_xyz': nan_array,
            'bias_xyz': nan_array
        }
        return dimension_features
    else:
        coordinates = np.asarray(coordinates)
        root_node = data.morphology.get_root()
        root_xyz = np.asarray([root_node['x'], root_node['y'], root_node['z']])
        coordinates = coordinates - root_xyz

        min_xyz = coordinates.min(axis=0)
        max_xyz = coordinates.max(axis=0)

        min_for_bias_xyz = min_xyz.copy()
        min_for_bias_xyz[min_for_bias_xyz > 0] = 0
        max_for_bias_xyz = max_xyz.copy()
        max_for_bias_xyz[max_for_bias_xyz < 0] = 0

        signed_bias_xyz = np.abs(max_for_bias_xyz) - np.abs(min_for_bias_xyz)
        bias_xyz = np.array([b if f else np.abs(b)
            for b, f in zip(signed_bias_xyz, signed_bias)])

        size = max_xyz - min_xyz
        dimension_features = {
            'width': size[0],
            'height': size[1],
            'depth': size[2],
            'min_xyz': min_xyz,
            'max_xyz': max_xyz,
            'bias_xyz': bias_xyz
        }
        return dimension_features
