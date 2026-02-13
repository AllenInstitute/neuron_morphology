from typing import Optional, List, Dict

import numpy as np

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    RequiresRoot,
    BifurcationFeatures,
    Geometric,
)
from neuron_morphology.feature_extractor.data import (
    MorphologyLike, get_morphology)
from neuron_morphology.morphology import Morphology


__all__ = [
    "num_outer_bifurcations",
    "calculate_outer_bifs",
    "mean_bifurcation_angle_local",
    "mean_bifurcation_angle_remote"
]


def calculate_outer_bifs(
    morphology: Morphology,
    soma: Dict,
    node_types: Optional[List[int]]
) -> int:

    """
        Counts the number of bifurcation points beyond the a sphere
        with 1/2 the radius from the soma to the most distant point
        in the morphology, with that sphere centered at the soma.

        Parameters
        ----------
        morphology: Describes the structure of a neuron
        soma: Must have keys "x", "y", and "z", describing the position of this
            morphology's soma in
        node_types: Restrict included nodes to these types. See
            neuron_morphology.constants for avaiable node types.

        Returns
        -------
        the number of bifurcations

    """

    nodes = morphology.get_node_by_types(node_types)
    far = 0
    for node in nodes:
        dist = morphology.euclidean_distance(soma, node)
        if dist > far:
            far = dist

    count = 0
    rad = far / 2.0
    for node in nodes:
        if len(morphology.children_of(node)) > 1:
            dist = morphology.euclidean_distance(soma, node)
            if dist > rad:
                count += 1
    return count


@marked(Geometric)
@marked(BifurcationFeatures)
@marked(RequiresRoot)
def num_outer_bifurcations(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> int:
    """ Feature Extractor interface to calculate_outer_bifurcations. Returns
    the number of bifurcations (branch points), excluding those too close to
    the root (threshold is 1/2 the max distance from the root to any node).

    Parameters
    ----------
    data : Holds a morphology object. No additional data is required
    node_types : Restrict included nodes to these types. See
        neuron_morphology.constants for avaiable node types.

    """

    return calculate_outer_bifs(
        data.morphology,
        data.morphology.get_root(),
        node_types
    )


def angle_between(v1, v2):
    """Helper function to get angle between two numpy vectors"""
    v1 = np.asarray(v1)
    v2 = np.asarray(v2)
    v1_u = v1 / np.linalg.norm(v1)
    v2_u = v2 / np.linalg.norm(v2)

    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


@marked(Geometric)
@marked(BifurcationFeatures)
def mean_bifurcation_angle_local(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> float:
    """
        Compute the average angle between child segments at
        bifurcations throughout the morphology.
        Trifurcations are ignored. Note: this introduces possible segmentation
        artifacts if trifurcations are due to large segment sizes.

        Parameters
        ----------
        data: The reconstruction whose max euclidean distance will be
            calculated
        node_types: restrict consideration to these types

        Returns
        -------

        Scalar value

    """
    morphology = get_morphology(data)
    total_angle = 0.0
    n = 0
    nodes = morphology.get_node_by_types(node_types)
    for node in nodes:
        if len(morphology.children_of(node)) == 2:
            node_vec = np.asarray([node['x'], node['y'], node['z']])

            a = morphology.children_of(node)[0]
            a_vec = np.asarray([a['x'], a['y'], a['z']])

            b = morphology.children_of(node)[1]
            b_vec = np.asarray([b['x'], b['y'], b['z']])

            total_angle += angle_between(a_vec - node_vec, b_vec - node_vec)
            n += 1

    if n == 0:
        return float('nan')
    return total_angle / n


@marked(Geometric)
@marked(BifurcationFeatures)
def mean_bifurcation_angle_remote(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> float:
    """
        Compute the average angle between the next branch point or terminal
        tip of child segments at each bifurcation.
        Trifurcations are ignored. Note: this introduces possible segmentation
        artifacts if trifurcations are due to large segment sizes.

        Parameters
        ----------

        Parameters
        ----------
        data: The reconstruction whose max euclidean distance will be
            calculated
        node_types: restrict consideration to these types


        Returns
        -------

        Scalar value, nan if no nodes

    """
    morphology = get_morphology(data)
    total_angle = 0.0
    n = 0
    nodes = morphology.get_node_by_types(node_types)
    for node in nodes:
        if len(morphology.children_of(node)) == 2:
            node_vec = np.asarray([node['x'], node['y'], node['z']])

            # find the point to measure to, whether it be the next
            #   branch point or tip
            a = morphology.children_of(node)[0]
            while len(morphology.children_of(a)) == 1:
                a = morphology.children_of(a)[0]
            a_vec = np.asarray([a['x'], a['y'], a['z']])

            b = morphology.children_of(node)[1]
            while len(morphology.children_of(b)) == 1:
                b = morphology.children_of(b)[0]
            b_vec = np.asarray([b['x'], b['y'], b['z']])

            total_angle += angle_between(a_vec - node_vec, b_vec - node_vec)
            n += 1

    if n == 0:
        return float('nan')
    return total_angle / n
