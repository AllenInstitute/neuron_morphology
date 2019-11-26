import math
import numpy as np
from neuron_morphology.features.common import calculate_kurtosis, calculate_skewness
from neuron_morphology.constants import SOMA


def calculate_compartment_moments(morphology, soma, node_types):

    """
        Calculates first and second moments of all compartments along each axis

        Parameters
        ----------

        morphology: Morphology object

        soma: dict
        soma node

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Two 3-element arrays. The first is the first moments on X,Y,Z. The
        second is the second moments on X,Y,Z.

    """
    nodes = morphology.get_node_by_types(node_types)
    compartment_list = morphology.get_compartments(nodes, node_types)
    values_x, values_y, values_z = calculate_values_for_compartments(morphology, soma, compartment_list)
    centroid = calculate_centroid_for_compartments(morphology, soma, compartment_list)
    second = calculate_second_for_compartments(morphology, soma, centroid, compartment_list)
    skew = calculate_skewness(values_x, values_y, values_z)
    kurtosis = calculate_kurtosis(values_x, values_y, values_z)
    return centroid, second, skew, kurtosis


def calculate_second_for_compartments(morphology, soma, centroid, compartment_list):

    second = np.zeros(3)
    compartment_list_length = len(compartment_list)
    norm = 0

    for compartment in compartment_list:
        if compartment[1]['type'] is SOMA:   # ignore soma compartments in this calculation
            continue
        dist = (soma['x'] + centroid[0]) - morphology.get_compartment_midpoint(compartment)[0]
        second[0] += dist * dist * morphology.get_compartment_length(compartment)
        #
        dist = (soma['y'] + centroid[1]) - morphology.get_compartment_midpoint(compartment)[1]
        second[1] += dist * dist * morphology.get_compartment_length(compartment)
        #
        dist = (soma['z'] + centroid[2]) - morphology.get_compartment_midpoint(compartment)[2]
        second[2] += dist * dist * morphology.get_compartment_length(compartment)
        norm += morphology.get_compartment_length(compartment)

    second /= 1.0 * (norm/compartment_list_length) * compartment_list_length
    return second


def calculate_centroid_for_compartments(morphology, soma, compartment_list):

    centroid = np.zeros(3)
    norm = 0
    compartment_list_length = len(compartment_list)
    for compartment in compartment_list:
        if compartment[1]['type'] is SOMA:   # ignore soma compartments in this calculation
            continue
        # make centroid relative to soma
        centroid[0] += (morphology.get_compartment_midpoint(compartment)[0] - soma['x']) * morphology.get_compartment_length(compartment)
        centroid[1] += (morphology.get_compartment_midpoint(compartment)[1] - soma['y']) * morphology.get_compartment_length(compartment)
        centroid[2] += (morphology.get_compartment_midpoint(compartment)[2] - soma['z']) * morphology.get_compartment_length(compartment)
        norm += morphology.get_compartment_length(compartment)
    # if no compartments, return null
    if norm == 0:
        empty = [float('nan'), float('nan'), float('nan')]
        return empty, empty, empty, empty
    # to get centroid we must divide by average compartment length and by
    #   number of compartments. this simplifies to being divided by
    #   summed compartment length. ie, centroid /= (norm/len) * len
    centroid /= 1.0 * (norm/compartment_list_length) * compartment_list_length
    return centroid


def calculate_values_for_compartments(morphology, soma, compartment_list):

    values_x = []
    values_y = []
    values_z = []
    for compartment in compartment_list:
        if compartment[1]['type'] is SOMA:   # ignore soma compartments in this calculation
            continue
        values_x.append(morphology.get_compartment_midpoint(compartment)[0] - soma['x'])
        values_y.append(morphology.get_compartment_midpoint(compartment)[1] - soma['y'])
        values_z.append(morphology.get_compartment_midpoint(compartment)[2] - soma['z'])

    return values_x, values_y, values_z


def calculate_compartment_moment_features(morphology, node_types):

    features = {}
    soma = morphology.get_root()
    moments = calculate_compartment_moments(morphology, soma, node_types)
    features["first_compartment_moment_x"] = moments[0][0]
    features["first_compartment_moment_y"] = moments[0][1]
    features["first_compartment_moment_z"] = moments[0][2]
    features["compartment_stdev_x"] = math.sqrt(moments[1][0])
    features["compartment_stdev_y"] = math.sqrt(moments[1][1])
    features["compartment_stdev_z"] = math.sqrt(moments[1][2])
    features["compartment_skew_x"] = moments[2][0]
    features["compartment_skew_y"] = moments[2][1]
    features["compartment_skew_z"] = moments[2][2]
    features["compartment_kurt_x"] = moments[3][0]
    features["compartment_kurt_y"] = moments[3][1]
    features["compartment_kurt_z"] = moments[3][2]

    return features
