import math
import numpy as np
from neuron_morphology.constants import SOMA, AXON


def unit_vector(vector):

    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):

    """ Returns the angle in radians between vectors 'v1' and 'v2'::

    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)

    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def calculate_axon_base(morphology, soma, node_types):

    """
        AXON-ONLY feature.
        Returns the relative radial position on the soma where the
        tree holding the axon connects to the soma. 0 is on the bottom,
        1 on the top, and 0.5 out a side.
        Also returns the distance between the axon root and the soma
        surface (0 if axon connects to soma, >0 if axon branches from
        dendrite).

        Parameters
        ----------

        morphology: Morphology object

        soma: dict
        soma node

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        (float, float):
        First value is relative position (height, on [0,1]) of axon
            tree on soma. Second value is distance of axon root from soma

    """

    # find axon node, get its tree ID, fetch that tree, and see where
    #   it connects to the soma radially
    nodes = morphology.get_node_by_types(node_types)
    tree_root = None
    dist = 0
    for node in nodes:
        prev_node = node
        # trace back to soma, to get stem root
        while morphology.parent_of(node)['type'] != SOMA:
            node = morphology.parent_of(node)
            if node['type'] == AXON:
                # this shouldn't happen, but if there's more axon toward
                #   soma, start counting from there
                prev_node = node
                dist = 0
            dist += morphology.euclidean_distance(prev_node, node)
            prev_node = node
        tree_root = node
        break

    # make point soma-radius north of soma root
    # do acos(dot product) to get angle of tree root from vertical
    # adjust so 0 is theta=pi and 1 is theta=0
    vert = np.zeros(3)
    vert[1] = 1.0
    root = np.zeros(3)
    root[0] = tree_root['x'] - soma['x']
    root[1] = tree_root['y'] - soma['y']

    # multiply in z scale factor

    root[2] = (tree_root['z'] - soma['z']) * 3.0
    theta = angle_between(vert, root) / math.pi
    return theta, dist


def calculate_axon_features(morphology, node_types):

    features = {}
    soma = morphology.get_root()
    rot, dist = calculate_axon_base(morphology, soma, node_types)
    features["soma_theta"] = rot
    features["soma_distance"] = dist

    return features
