import math
import numpy as np
from neuron_morphology.features.common import calculate_kurtosis, calculate_skewness
from neuron_morphology.constants import SOMA


def calculate_bifurcation_moments(morphology, soma, node_types):

    nodes = morphology.get_node_by_types(node_types)
    centroid = calculate_centroid(morphology, soma, nodes)
    empty = [float('nan'), float('nan'), float('nan')]
    if centroid is None:
        return empty, empty, empty, empty
    values_x, values_y, values_z = calculate_values(morphology, soma, nodes)
    second = calculate_second(morphology, centroid, soma, nodes)
    skew = calculate_skewness(values_x, values_y, values_z)
    kurtosis = calculate_kurtosis(values_x, values_y, values_z)
    centroid[0] = abs(centroid[0])
    centroid[2] = abs(centroid[2])
    return centroid, second, skew, kurtosis


def calculate_centroid(morphology, soma, nodes):

    """
        Calculates first moments of all bifurcating compartments
        (compartments with 2 or more children) along each axis

        Parameters
        ----------

        morphology: Morphology object

        soma: dict
        soma node

        nodes: list
        list of nodes to use for calculating centroid

        Returns
        -------

        Two 3-element arrays. The first is the first moments on X,Y,Z.

    """

    centroid = np.zeros(3)
    n = 0
    for node in nodes:
        if node['type'] == SOMA:
            continue
        if len(morphology.children_of(node)) > 1:
            centroid[0] += node['x'] - soma['x']
            centroid[1] += node['y'] - soma['y']
            centroid[2] += node['z'] - soma['z']
            n += 1
    if n == 0:
        return None
    centroid /= 1.0 * n
    return centroid


def calculate_second(morphology, centroid, soma, nodes):

    """
        Calculates second moments of all bifurcating compartments
        (compartments with 2 or more children) along each axis

        Parameters
        ----------

        morphology: Morphology object

        centroid: 3-element list
        centroid of the morphology object

        soma: dict
        soma node

        nodes: list
        list of nodes to use for calculating second

        Returns
        -------

        Two 3-element arrays. The first is the second moments on X,Y,Z.

    """

    second = np.zeros(3)
    n = 0
    for node in nodes:
        children_nodes = morphology.children_of(node)
        if len(children_nodes) > 1:
            # x
            dist = (centroid[0] + soma['x']) - node['x']
            second[0] += dist * dist
            # y
            dist = (centroid[1] + soma['y']) - node['y']
            second[1] += dist * dist
            # z
            dist = (centroid[2] + soma['z']) - node['z']
            second[2] += dist * dist
            n += 1

    second /= 1.0 * n
    return second


def calculate_values(morphology, soma, nodes):

    """
        Calculates the values used for calculating skewness and kurtosis

        Parameters
        ----------

        morphology: Morphology object

        soma: dict
        soma node

        nodes: list
        list of nodes to use for calculating values

        Returns
        -------

        tuple of lists of x,y,z values used for calculating skewness and kurtosis

    """

    values_x = []
    values_y = []
    values_z = []
    for node in nodes:
        if node['type'] == SOMA:
            continue
        children_nodes = morphology.children_of(node)
        if len(children_nodes) > 1:
            values_x.append(node['x'] - soma['x'])
            values_y.append(node['y'] - soma['y'])
            values_z.append(node['z'] - soma['z'])

    return values_x, values_y, values_z


def calculate_bifurcation_moment_features(morphology, node_types):

    features = {}
    soma = morphology.get_root()
    moments = calculate_bifurcation_moments(morphology, soma, node_types)
    features["first_bifurcation_moment_x"] = moments[0][0]
    features["first_bifurcation_moment_y"] = moments[0][1]
    features["first_bifurcation_moment_z"] = moments[0][2]
    features["bifurcation_stdev_x"] = math.sqrt(moments[1][0])
    features["bifurcation_stdev_y"] = math.sqrt(moments[1][1])
    features["bifurcation_stdev_z"] = math.sqrt(moments[1][2])
    features["bifurcation_skew_x"] = moments[2][0]
    features["bifurcation_skew_y"] = moments[2][1]
    features["bifurcation_skew_z"] = moments[2][2]
    features["bifurcation_kurt_x"] = moments[3][0]
    features["bifurcation_kurt_y"] = moments[3][1]
    features["bifurcation_kurt_z"] = moments[3][2]

    return features
