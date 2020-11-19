import math
import numpy as np

from functools import partial
from typing import Optional, List, Dict
from neuron_morphology.feature_extractor.marked_feature import (
    MarkedFeature, marked
)
from neuron_morphology.feature_extractor.mark import (
    RequiresRoot,
    RequiresSoma,
    RequiresRelativeSomaDepth,
    RequiresApical,
    RequiresBasal,
    RequiresAxon,
    RequiresDendrite,
    Geometric
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.constants import (
    SOMA, AXON, BASAL_DENDRITE, APICAL_DENDRITE
)
from neuron_morphology.morphology import Morphology


__all__ = [
    "calculate_soma_surface",
    "calculate_relative_soma_depth",
    "calculate_soma_features",
    "calculate_stem_exit_and_distance"
]


@marked(Geometric)
@marked(RequiresRoot)
def calculate_soma_surface(data: Data) -> float:

    """
        Approximates the surface area of the soma. Morphologies with only
        a single soma node are supported.

        Parameters
        ----------
        data: Data Object containing a morphology

        Returns
        -------

        Scalar value

    """

    soma = data.morphology.get_soma()
    return 4.0 * math.pi * soma['radius'] * soma['radius']


@marked(RequiresRoot)
@marked(RequiresRelativeSomaDepth)
def calculate_relative_soma_depth(data: Data) -> float:
    """
        Calculate the soma depth relative to pia/wm

        Parameters
        ----------
        data: Data Object containing a morphology

        Returns
        -------

        Scalar value

    """

    return data.relative_soma_depth


@marked(Geometric)
@marked(RequiresRoot)
@marked(RequiresRelativeSomaDepth)
def calculate_soma_features(data: Data):
    """
        Calculate the soma features

        Parameters
        ----------
        data: Data Object containing a morphology

        Returns
        -------

        soma_features

    """

    features = {}
    features["soma_surface"] = calculate_soma_surface(data.morphology)
    features["relative_soma_depth"] = calculate_relative_soma_depth(data)

    return features


@marked(Geometric)
@marked(RequiresSoma)
@marked(RequiresRoot)
def calculate_stem_exit_and_distance(data: Data, node_types: Optional[List[int]], z_scale=3.0):
    """
        Returns the relative radial position (stem_exit) on the soma where the
        tree holding the tree connects to the soma. 0 is on the bottom,
        1 on the top, and 0.5 out a side.
        Also returns the distance (stem_distance) between the tree root and the
        soma surface.

        Parameters
        ----------

        data: Data Object containing a morphology

        soma: dict
        soma node

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        (float, float):
        First value is relative position (height, on [0,1]) of a
        tree on soma. Second value is distance of the root from soma

    """

    # find axon node, get its tree ID, fetch that tree, and see where
    #   it connects to the soma radially
    nodes = data.morphology.get_node_by_types(node_types)

    node_ids = [data.morphology.node_id_cb(n) for n in nodes]
    tree_root = None
    stem_distance = 0
    stem_exit = 0

    soma = data.morphology.get_soma()

    # find all root nodes (meaning a node whose parent is not in the set of nodes under consideration)
    root_nodes = []
    for node in nodes:
        if data.morphology.parent_id_cb(node) not in node_ids:
            root_nodes.append(node)

    # set the root node closest to soma as the tree_root
    stem_exit_info = []
    for node in root_nodes:
        if data.morphology.parent_id_cb(node) == data.morphology.node_id_cb(soma):
            stem_distance = 0
        else:
            stem_distance = data.morphology.euclidean_distance(node, soma)

        # make point soma-radius north of soma root
        # do acos(dot product) to get angle of tree root from vertical
        # adjust so 0 is theta=pi and 1 is theta=0
        vert = np.zeros(3)
        vert[1] = 1.0
        root = np.zeros(3)
        root[0] = node['x'] - soma['x']
        root[1] = node['y'] - soma['y']
        root[2] = (node['z'] - soma['z']) * z_scale
        stem_exit = np.arccos(np.clip(np.dot(vert/np.linalg.norm(vert), root/np.linalg.norm(root)), -1.0, 1.0)) / math.pi

        stem_exit_info.append((stem_exit, stem_distance))

    return stem_exit_info


@marked(RequiresSoma)
@marked(RequiresRoot)
def calculate_number_of_stems(data: Data, node_types: Optional[List[int]]):

    """
        Calculate the number of soma stems.
        This is defined as the total number of non-soma child nodes on soma nodes.

        Parameters
        ----------
        data: Data Object containing a morphology

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    soma = data.morphology.get_soma()
    if node_types:
        return len(data.morphology.get_children_of_node_by_types(soma, node_types))
    else:
        return len(data.morphology.children_of(soma))

@marked(Geometric)
@marked(RequiresRoot)
def soma_percentile(data: Data,
                    node_types: Optional[List[int]],
                    symmetrize_xz: bool = True):
    """
        Calculates the percent of of nodes that are below the soma.
        If symmetrize_xz is true, then p

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

        symmetrize_xz: bool indicating that x and z percentages should always
                       fall between 0 and 0.5 to prevent handedness
                       (e.g if 0.75 nodes are below the soma in the
                        x direction, then return 1-0.75=0.25 instead)


        Returns
        -------

        percentiles: array of x, y, and z percentiles

    """
    soma_node = data.morphology.get_root()
    soma_coord = np.asarray([soma_node['x'], soma_node['y'], soma_node['z']])

    nodes = data.morphology.get_node_by_types(node_types=node_types)
    coords = np.asarray([[node['x'], node['y'], node['z']] for node in nodes])

    num_less_than = coords < soma_coord
    percentile = num_less_than.sum(axis=0) / num_less_than.shape[0]

    if symmetrize_xz:
        if percentile[0] > 0.5:
            percentile[0] = 1.0 - percentile[0]
        if percentile[2] > 0.5:
            percentile[2] = 1.0 - percentile[2]

    return percentile


@marked(Geometric)
@marked(RequiresSoma)
@marked(RequiresRoot)
def calculate_stem_exit_histogram(data: Data, node_types: Optional[List[int]]):
    """
        Returns the normalized stem exit count for each exit direction (side more,
        side less, up and down). Sum of these values will  equal one.
        The "more" and "less" sides are created to prevent "left or right handedness."

        Parameters
        ----------
        data: Data Object containing a morphology
        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to
        Returns
        -------
        stem_exit_histograms: dict containing normalized stem exit values
    """
    soma_node = data.morphology.get_soma()
    stems = [node for node in data.morphology.get_children(soma_node) if node['type'] in node_types]
    vert_vect = np.array([0,1])

    hist_dict = {"up":0,
                "down":0,
                "left":0,
                "right":0}

    for stem_node in stems:
        stem_vector = np.array([stem_node['x'] - soma_node['x'], stem_node['y']-soma_node['y']])
        stem_unit_vector = stem_vector/np.linalg.norm(stem_vector)
        theta = np.arccos(np.clip(np.dot(vert_vect, stem_unit_vector), -1.0, 1.0))

        if theta < np.pi / 4: # up
            hist_dict["up"] += 1
        elif theta < 3 * np.pi / 4: # left/right
            if stem_node['x'] < soma_node['x']:
                hist_dict["left"] += 1
            else:
                hist_dict["right"] += 1
        else:
            hist_dict["down"] += 1

    n_stems = float(len(stems))
    if n_stems == 0:
        return {"up": 0, "down": 0, "side_more": 0, "side_less": 0}

    stem_exit_histogram = {"up": hist_dict["up"] / n_stems,
                           "down": hist_dict["down"] / n_stems
                          }

    if hist_dict["left"] > hist_dict["right"]:
        stem_exit_histogram["side_more"] = hist_dict["left"] / n_stems
        stem_exit_histogram["side_less"] = hist_dict["right"] / n_stems
    else:
        stem_exit_histogram["side_more"] = hist_dict["right"] / n_stems
        stem_exit_histogram["side_less"] = hist_dict["left"] / n_stems

    return stem_exit_histogram

