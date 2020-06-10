from typing import Optional, List, Dict

from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)

from neuron_morphology.feature_extractor.mark import RequiresRoot, Geometric
from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.data import (
    MorphologyLike, get_morphology)


# TODO: There is a breadth_first_traversal method defined on Morphology. We
# should use that here
def _calculate_max_path_distance(morphology, root, node_types):
    # if root not specified, grab the soma root if it exists, and the
    #   root of the first disconnected tree if not

    if node_types is None:
        node_types = [SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE]

    if root is None:
        root = morphology.get_root()
    total_length = 0.0
    # sum up length for all child compartments
    max_tip_type = None
    while len(morphology.get_children(root)) > 0:
        # the next node is a continuation from this node (ie, no
        #   bifurcation). update path length and evaluate the
        #   next node
        # path tracing is done using nodes. if a node is associated
        #   with a compartment (all non-root nodes are) then add that
        #   compartment's length to the accumulated distance
        if len(morphology.get_children(root)) == 1:
            # get length of associated compartment, if it exists, and if
            #   it's not soma
            if root['type'] != SOMA:
                compartment = morphology.get_compartment_for_node(root)
                if compartment:
                    total_length += morphology.get_compartment_length(compartment)
            root = morphology.get_children(root)[0]
        else:
            # we reached a bifurcation point
            # recurse to find length of each child branch and then
            #   exit loop
            max_sub_dist = 0.0
            children_of_root = morphology.get_children(root)
            for child in children_of_root:
                dist, tip_type = _calculate_max_path_distance(morphology, child, node_types)
                if dist > max_sub_dist and tip_type in node_types:
                    max_sub_dist = dist
                    max_tip_type = tip_type
            total_length += max_sub_dist
            break
    # the length of this compartment hasn't been included yet, and if it
    #   isn't part of the soma
    if max_tip_type is None:
        max_tip_type = root["type"]
    if root['type'] != SOMA:
        compartment = morphology.get_compartment_for_node(root)
        if compartment:
            total_length += morphology.get_compartment_length(compartment)
    return total_length, max_tip_type


def calculate_max_path_distance(morphology, root, node_types=None):
    """ Helper for max_path_distance. See below for more information.
    """

    max_path = 0.0
    root_children = morphology.get_children(root)
    if root_children is None:
        return float('nan')
    for node in root_children:
        path, tip_type = _calculate_max_path_distance(morphology, node, node_types)
        if path > max_path:
            if node_types and tip_type in node_types:
                max_path = path
            else:
                max_path = path
    return max_path


@marked(RequiresRoot)
@marked(Geometric)
def max_path_distance(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> float:

    """ Calculate the distance, following the path of adjacent neurites, from
    the soma to the furthest compartment. This is equivalent to the distance
    to the furthest SWC node.

    Parameters
    ----------
    data : the input reconstruction
    node_types : if provided, restrict the calculation to nodes of these
        types

    Returns
    -------
    The along-path distance from the soma to the farthest (in the along-path
    sense) node.

    """

    morphology = get_morphology(data)
    return calculate_max_path_distance(
        morphology,
        morphology.get_root(),
        node_types
    )


@marked(RequiresRoot)
@marked(Geometric)
def early_branch_path(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None,
    soma: Optional[Dict] = None
) -> float:
    """ Returns the ratio of the longest 'short' branch from a bifurcation to
    the maximum path length of the tree. In other words, for each bifurcation,
    the maximum path length below that branch is calculated, and the shorter of
    these values is used. The maximum of these short values is divided by the
    maximum path length.

    Parameters
    ----------
    data : the input reconstruction
    node_types : if provided, restrict the calculation to nodes of these
        types
    soma : if provided, use this node as the root, otherwise infer the root
        from the argued morphology

    Returns
    -------
    ratio of max short branch to max path length

    """

    morphology = get_morphology(data)
    soma = soma or morphology.get_root()

    path_len = _calculate_max_path_distance(morphology, soma, node_types)[0]
    if path_len == 0:
        return 0.0

    nodes = morphology.get_node_by_types(node_types)
    longest_short = 0.0

    for node in nodes:
        if len(morphology.get_children(node, node_types)) < 2:
            continue

        current_short = min(
            _calculate_max_path_distance(morphology, child, node_types)[0]
            for child in morphology.children_of(node)
        )

        longest_short = max(longest_short, current_short)

    return longest_short / path_len


def _calculate_mean_contraction(morphology, reference, root, node_types):

    """
        Calculate the average contraction of all sections. In other words,
        calculate the average ratio of euclidean distance to path distance
        between all bifurcations in the morphology. Trifurcations are treated
        as bifurcations.

        Parameters
        ----------

        morphology: Morphology object

        reference: dict
        This is the node of the previous bifurcation

        root: dict
        This is the node from which to measure branch contraction under

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Two scalars: euclidean distance, path distance
        These are the total bif-bif and bif-tip distances under this root

    """
    # advance to next bifurcation or tip and measure distance to
    #   reference location
    # on bifurcation, recurse into this function again
    # treat trifurcation as 2 successive bifs
    euc_dist = 0
    path_dist = morphology.euclidean_distance(reference, root)
    tot_path = 0.0
    tot_euc = 0.0
    while len(morphology.get_children(root, node_types)) > 0:
        # if the next compartment is a continuation (ie, no
        #   bifurcation) then get the next node
        if len(morphology.get_children(root, node_types)) == 1:
            next_node = morphology.get_children(root, node_types)[0]
            path_dist += morphology.euclidean_distance(root, next_node)
            root = next_node
        else:
            # we reached a bifurcation point. recurse and analyze children
            for child in morphology.get_children(root, node_types):
                euc, path = _calculate_mean_contraction(morphology, root, child, node_types)
                tot_euc += euc
                tot_path += path
            break
    euc_dist += morphology.euclidean_distance(root, reference)
    return tot_euc + euc_dist, tot_path + path_dist


def calculate_mean_contraction(morphology, root=None, node_types=None):
    """ See mean_contraction
    """
    roots = morphology.get_roots_for_analysis(root, node_types)
    if roots is None:
        return float('nan')
    euc_dist = 0.0
    path_dist = 0.0
    for ref in roots:
        # advance to next bifurcation
        while len(morphology.get_children(ref, node_types)) == 1:
            ref = morphology.get_children(ref, node_types)[0]
        if len(morphology.get_children(ref, node_types)) == 0:
            continue
        # analyze each branch from this bifurcation point
        for child in morphology.get_children(ref, node_types):
            euc, path = _calculate_mean_contraction(morphology, ref, child, node_types)
            euc_dist += euc
            path_dist += path
    if path_dist == 0.0:
        return float('nan')
    return 1.0 * euc_dist / path_dist


@marked(Geometric)
@marked(RequiresRoot)
def mean_contraction(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculate the average contraction of all sections. In other words,
    calculate the average ratio of euclidean distance to path distance
    between all bifurcations in the morphology. Trifurcations are treated
    as bifurcations.

    Parameters
    ----------
    data : the input reconstruction
    node_types : if provided, restrict the calculation to nodes of these
        types

    Returns
    -------
    The average contraction across all sections in this reconstruction

    """

    morphology = get_morphology(data)
    return calculate_mean_contraction(
        morphology,
        None,
        node_types
    )