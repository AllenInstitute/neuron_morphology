from typing import Optional, List

import numpy as np
from scipy import stats
from scipy.spatial import distance

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import Geometric,RequiresRoot


@marked(Geometric)
@marked(RequiresRoot)
def moments_along_max_distance_projection(
            data: Data,
            node_types: Optional[List] = None,
            coord_type: COORD_TYPE = COORD_TYPE.BIFURCATION,
            ):
    """
        Calculate the distance projections of a specific compartment and coordinate type along
        the line segment connecting soma to the most distant (from soma) node of that compartment.

        Parameters
        ----------
        data: Data Object containing a morphology
        node_types: a list of node types (see neuron_morphology constants)
        coord_type: Restrict which coordinate types are measured (i.e. projected along line segment)
                            (see neuron_morphology.features.statistics.coordinates for options)

        Returns
        -------
        summary_dict: summary stats of distances projected along specified line segment
    """

    morphology = data.morphology
    find_most_distant_coordinates = COORD_TYPE.NODE.get_coordinates(morphology, node_types=node_types)
    measuring_coordinates = coord_type.get_coordinates(morphology, node_types=node_types)

    if (not find_most_distant_coordinates) or (not measuring_coordinates):
        summary_dict = {
            'mean': np.nan,
            'std': np.nan,
            'var': np.nan,
            'skew': np.nan,
            'kurt': np.nan}

    else:
        measuring_coordinates = np.asarray(measuring_coordinates)
        soma_node = morphology.get_soma()
        soma_coord = np.array([soma_node['x'],soma_node['y'],soma_node['z']])

        max_distance = -1
        for coord in find_most_distant_coordinates:
            dist = distance.euclidean(coord,soma_coord)
            if dist>max_distance:
                max_distance = dist
                furthest_coord = coord

        projected_dists = np.dot( (furthest_coord - soma_coord).T, (measuring_coordinates - soma_coord).T )
        norm = np.linalg.norm(furthest_coord - soma_coord)

        distances = projected_dists/norm
        distances /= max_distance
        (_, _, mean, variance, skew, kurt) = stats.describe(distances, axis=0)
        stdv = np.std(distances)

        summary_dict = {
                'mean': mean,
                'std': stdv,
                'var': variance,
                'skew': skew,
                'kurt': kurt}

    return summary_dict

