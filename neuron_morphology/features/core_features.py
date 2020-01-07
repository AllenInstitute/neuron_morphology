import math
from importlib import import_module

from allensdk.deprecated import deprecated

from neuron_morphology.constants import *
from neuron_morphology.features.common import calculate_max_euclidean_distance
from neuron_morphology.features.path import _calculate_max_path_distance


def shim_import(module_path: str, name: str, message: str):
    """ Imports and deprecates a function

    Parameters
    ----------
    module_path : dot-notation import path for the module containing the 
        function of interest
    name : name of the function. Note that the object must actually be a 
        function!
    message : The message to be displayed as part of the 
        VisibleDeprecationWarning raised when calling this function

    Returns
    -------
    the wrapped function

    """
    module = import_module(module_path)
    deprecator = deprecated(message)
    return deprecator(getattr(module, name))

# shims for backwards compatibility
calculate_outer_bifs = shim_import(
    "neuron_morphology.features.branching.outer_bifurcations",
    "calculate_outer_bifs",
    "use neuron_morphology.features.branching.outer_bifurcations instead"
)
calculate_max_path_distance = shim_import(
    "neuron_morphology.features.path",
    "calculate_max_path_distance",
    "use neuron_morphology.features.path.max_path_distance instead"
)
calculate_early_branch_path = shim_import(
    "neuron_morphology.features.path",
    "early_branch_path",
    "use neuron_morphology.features.path.early_branch_path instead"
)
calculate_mean_contraction = shim_import(
    "neuron_morphology.features.path",
    "calculate_mean_contraction",
    "use neuron_morphology.features.path.mean_contraction instead"
)
calculate_early_branch_path = shim_import(
    "neuron_morphology.features.path",
    "early_branch_path",
    "use neuron_morphology.features.path.early_branch_path instead"
)


def calculate_number_of_stems(morphology):

    """
        Calculate the number of soma stems.
        This is defined as the total number of non-soma child nodes on soma nodes.

        Parameters
        ----------

        morphology: Morphology object

        Returns
        -------

        Scalar value

    """

    soma = morphology.get_root()
    return len(morphology.children_of(soma))


def calculate_number_of_stems_by_type(morphology, node_types):

    """
        Calculate the number of soma stems.
        This is defined as the total number of non-soma child nodes on soma nodes.

        Parameters
        ----------
        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    soma = morphology.get_root()
    return len(morphology.get_children_of_node_by_types(soma, node_types))


def calculate_number_of_tips(morphology, node_types):

    """
        Counts the number of endpoints (ie, non-soma nodes that have no children)

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)
    tips = 0
    for node in nodes:
        children = morphology.children_of(node)
        if node['type'] is not SOMA and len(children) == 0:
            tips += 1
    return tips


@deprecated("use size.total_length instead")
def calculate_total_length(morphology, node_types):

    """
        Calculate the total length of all segments in the morphology
        Parameters
        ----------
        morphology: Morphology object
        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to
        Returns
        -------
        Scalar value
    """

    total_length = 0.0

    # sum the length of all compartments, excluding the case where the
    #   parent node is the soma root, as that compartment should heavily
    #   overlap the soma. Include non-soma-root parents, as those will
    #   be assumed to be on (at least nearer) the soma surface
    nodes = morphology.get_node_by_types(node_types)
    compartment_list = morphology.get_compartments(nodes, node_types)
    for compartment in compartment_list:
        first_node_in_compartment = compartment[0]
        if first_node_in_compartment['type'] is SOMA and not morphology.parent_of(first_node_in_compartment):
            continue
        total_length += morphology.get_compartment_length(compartment)

    return total_length


def calculate_number_of_neurites(morphology, node_types):

    """
        Returns the number of non-soma nodes in the morphology

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)

    return len(nodes)


# TODO: this function claims to exclude soma nodes, but does not do so. We need 
# to determine which behavior is correct
@deprecated("use size.mean_diameter instead")
def calculate_mean_diameter(morphology, node_types):

    """
        Calculates the average diameter of all non-soma nodes.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)

    total = 0.0
    for node in nodes:
        total += 2.0 * node['radius']

    return 1.0 * total / len(nodes)


# TODO deprecate in favor of calculate_num_branches()
def calculate_number_of_bifurcations(morphology, node_types):

    """
        Calculates the number of bifurcating nodes in the morphology.
        A bifurcation is defined as a non-soma node having 2 child nodes.

        Parameters
        ----------
        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)

    bifurcations = 0
    for node in nodes:
        if len(morphology.children_of(node)) == 2:
            bifurcations += 1

    return bifurcations


def _calculate_position_relative_to_soma(morphology, node):

    soma = morphology.get_root()
    node['x'] = node['x'] - soma['x']
    node['y'] = node['y'] - soma['y']
    node['z'] = node['z'] - soma['z']
    return node


@deprecated("see size.mean_parent_daughter_ratio instead")
def calculate_mean_parent_daughter_ratio(morphology, node_types):

    """
        Returns the average ratio of child diameter to parent diameter.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)
    total = 0.0
    cnt = 0.0
    try:
        for node in nodes:
            children = morphology.children_of(node)
            if len(children) < 2:
                continue
            child_radii = 0.0
            for child in children:
                child_radii += child['radius']
            child_radii /= 1.0 * len(children)
            total += child_radii / node['radius']
            cnt += 1.0
    except ZeroDivisionError:
        # node radius was zero?
        cnt = 0
    if cnt == 0:
        return float('nan')
    return total / cnt


# TODO deprecate as duplicate calculate_mean_parent_daughter_ratio()
def calculate_parent_daughter_ratio(morphology, node_types, root=None):

    """
        Compute the average ratio of parent node to daughter node at
        each branch point.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        root: dict
        This is the node from which to analyze parent-daughter ratio under.
        When root=None, the soma is used.

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)
    if root is None:
        # if root not specified, grab the soma root if it exists, and the
        #   root of the first disconnected tree if not
        root = morphology.get_root()
    ratio_sum = 0.0
    n = 0
    try:
        for parent in nodes:
            if len(morphology.children_of(parent)) > 1:
                for daughter in morphology.children_of(parent):
                    ratio = daughter['radius'] / parent['radius']
                    ratio_sum += ratio
                    n += 1
    except ZeroDivisionError:
        n = 0   # node radius is zero. uncomputable
    if n == 0:
        return float('nan')
    return 1.0 * ratio_sum / n


def calculate_bifurcation_angle_local(morphology, node_types):

    """
        Compute the average angle between child segments at
        bifurcations throughout the morphology.
        Trifurcations are ignored. Note: this introduces possible segmentation
        artifacts if trifurcations are due to large segment sizes.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to


        Returns
        -------

        Scalar value

    """

    angle = 0.0
    n = 0.0
    nodes = morphology.get_node_by_types(node_types)
    try:
        for node in nodes:
            if len(morphology.children_of(node)) == 2:
                a = morphology.children_of(node)[0]
                ax = a['x'] - node['x']
                ay = a['y'] - node['y']
                az = a['z'] - node['z']
                b = morphology.children_of(node)[1]
                bx = b['x'] - node['x']
                by = b['y'] - node['y']
                bz = b['z'] - node['z']
                dot = ax*bx + ay*by + az*bz
                len_a = math.sqrt(ax*ax + ay*ay + az*az)
                len_b = math.sqrt(bx*bx + by*by + bz*bz)
                # ABS-42 -- floating point rounding error can cause acos()
                #   parameter to have absolute value slightly greater than
                #   1.0
                val = dot / (len_a * len_b)
                if val < -1.0:
                    val = -1.0
                elif val > 1.0:
                    val = 1.0
                theta = 180.0 * math.acos(val) / math.pi
                angle += theta
                n += 1.0
    except ZeroDivisionError:
        # probably a case of parent-child segment having zero length
        n = 0.0
        pass
    if n == 0.0:
        return float('nan')
    return 1.0 * angle / n


@deprecated("use size.total_surface and size.total_volume instead")
def calculate_total_size(morphology, node_types):

    """
        Calculates the total surface area and volume of non-soma compartments.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Two scalar values: total surface, total volume

    """
    total_sfc = 0.0
    total_vol = 0.0
    nodes = morphology.get_node_by_types(node_types)
    compartments = morphology.get_compartments(nodes, node_types)
    for compartment in compartments:
        node_1 = compartment[0]
        node_2 = compartment[1]
        if node_1['type'] is SOMA:
            continue
        r1 = node_1['radius']
        r2 = node_2['radius']
        compartment_length = morphology.get_compartment_length(compartment)
        total_sfc += 2.0 * math.pi * (0.5 * (r1 + r2)) * compartment_length
        DR = r2 - r1
        L = compartment_length
        vol = math.pi * (L*r1*r1 + L*DR + L*DR*DR/3.0)
        total_vol += vol
    return total_sfc, total_vol


def calculate_bifurcation_angle_remote(morphology, node_types):

    """
        Compute the average angle between the next branch point or terminal
        tip of child segments at each bifurcation.
        Trifurcations are ignored. Note: this introduces possible segmentation
        artifacts if trifurcations are due to large segment sizes.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    angle = 0.0
    n = 0.0
    nodes = morphology.get_node_by_types(node_types)
    for node in nodes:
        if len(morphology.children_of(node)) == 2:
            # find the point to measure to, whether it be the next
            #   branch point or tip
            a = morphology.children_of(node)[0]
            while len(morphology.children_of(a)) == 1:
                a = morphology.children_of(a)[0]
            ax = a['x'] - node['x']
            ay = a['y'] - node['y']
            az = a['z'] - node['z']
            b = morphology.children_of(node)[1]
            while len(morphology.children_of(b)) == 1:
                b = morphology.children_of(b)[0]
            bx = b['x'] - node['x']
            by = b['y'] - node['y']
            bz = b['z'] - node['z']
            dot = ax*bx + ay*by + az*bz
            len_a = math.sqrt(ax*ax + ay*ay + az*az)
            len_b = math.sqrt(bx*bx + by*by + bz*bz)
            theta = 180.0 * math.acos(dot / (len_a * len_b)) / math.pi
            angle += theta
            n += 1.0
    if n == 0.0:
        return float('nan')
    return 1.0 * angle / n


def _calculate_mean_fragmentation(morphology, root, node_types, initial_seg=False):

    """
        Compute the average number of compartments between successive
        branch points. Trifurcations are treated as bifurcations.
        NOTE: this feature is directly dependent on segmentation policy
        and will likely change whenever a morphology is resegmented.

        Parameters
        ----------

        morphology: Morphology object

        root: dict
        This is the node from which to count branch contraction under.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        initial_seg: Boolean
        True on entry, where the segment up to the next bif is not counted,
        and False otherwise (default)

        Returns
        -------

        Two scalars: num compartments, num branches

    """
    # count compartments between bifs and bifs, and between bifs and tips
    # on bifurcation, recurse into this function again
    child_branches = 0
    child_comparts = 0
    local_branches = 0
    local_comparts = 0
    while True:
        # if the next compartment is a continuation (ie, no
        #   bifurcation) then get the next node
        if len(morphology.get_children(root, node_types)) >= 2:
            # we reached a bifurcation point
            # recurse to find the number of branches along each path
            #   exit loop
            if not initial_seg:
                local_comparts += 1
                if local_branches == 0:
                    local_branches = 1
            for child in morphology.get_children(root, node_types):
                if root['type'] is SOMA:
                    initial = True
                else:
                    initial = False
                branches, cnt = _calculate_mean_fragmentation(morphology, child, node_types, initial)
                child_branches += branches
                child_comparts += cnt
            break
        else:
            if not initial_seg:
                local_comparts += 1
                if local_branches == 0:
                    local_branches = 1
            if len(morphology.children_of(root)) == 0:
                break
            root = morphology.children_of(root)[0]
    # we make it here when we're at a tip or when a bifurcation has
    #   been analyzed
    return local_branches + child_branches, local_comparts + child_comparts


def calculate_mean_fragmentation(morphology, root=None, node_types=None):

    """
        Compute the average number of compartments between successive
        branch points and between branch points and tips.
        Trifurcations are treated as bifurcations.
        NOTE: This feature is directly dependent on segmentation policy
        and will likely change whenever a morphology is resegmented.

        Parameters
        ----------

        morphology: Morphology object

        root: dict
        This is the node from which to count branches under.
        When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    roots = morphology.get_roots_for_analysis(root, node_types)
    if roots is None:
        return float('nan')
    n_branches = 0.0
    n_compartments = 0.0
    for node in roots:
        br, comp = _calculate_mean_fragmentation(morphology, node, node_types, True)
        n_branches += br
        n_compartments += comp
    if n_branches == 0.0:
        return float('nan')
    return 1.0 * n_compartments / n_branches


def _calculate_max_branch_order(morphology, root, node_types):
    # advance to next bifurcation or tip and increment counter
    # on bifurcation, recurse into this function again
    # treat trifurcation as 2 successive bifs
    num_branches = 0
    while len(morphology.get_children(root, node_types)) > 0:
        # if the next compartment is a continuation (ie, no
        #   bifurcation) then get the next node
        if len(morphology.get_children(root, node_types)) == 1:
            root = morphology.get_children(root, node_types)[0]
        elif len(morphology.get_children(root, node_types)) > 1:
            # if this isn't a soma node then it's time to increment branch count
            if root['type'] is not SOMA:
                num_branches += 1
            # we reached a bifurcation point
            # recurse to find the number of branches along each path
            #   exit loop
            max_depth = 0
            for child in morphology.get_children(root, node_types):
                branches = _calculate_max_branch_order(morphology, child, node_types)
                if branches > max_depth:
                    max_depth = branches
            num_branches += max_depth
            break
    return num_branches


def calculate_max_branch_order(morphology, root=None, node_types=None):

    """ Calculate the maximum number of branches that exist between
        the root and the furthest (deepest) tip.

        Parameters
        ----------

        morphology: Morphology object

        root: dict
        This is the node from which to count branches under.
        When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value
    """
    max_order = 0
    roots = morphology.get_roots_for_analysis(root, node_types)
    if roots is None:
        return float('nan')
    for node in roots:
        order = _calculate_max_branch_order(morphology, node, node_types)
        if order > max_order:
            max_order = order
    return max_order


def _calculate_number_of_branches(morphology, root, node_types):

    """
        Calculate the number of branches. A branch is defined as one
        or more compartments that lie between bifurcations or between a
        bifurcation and a termination point.
        The soma is considered a bifurcation point, regardless of how many
        stems it has.

        Parameters
        ----------

        morphology: Morphology object

        root: dict
        This is the node from which to count branches under.
        When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    # advance to next bifurcation or tip and increment counter
    # on bifurcation, recurse into this function again
    # treat trifurcation as 2 successive bifs
    num_branches = 0
    while len(morphology.get_children(root, node_types)) > 0:
        # if the next compartment is a continuation (ie, no
        #   bifurcation) then get the next node
        if len(morphology.get_children(root, node_types)) == 1:
            root = morphology.get_children(root, node_types)[0]
        else:
            if root['type'] != SOMA and len(morphology.get_children(root, node_types)) > 2:
                # treat trifurcation as successive bifs and increment
                #   branch counter to acknowledge implicit branch
                num_branches += len(morphology.get_children(root, node_types)) - 2
            # we reached a bifurcation point
            # recurse to find the number of branches along each path
            #   exit loop
            for child in morphology.get_children(root, node_types):
                num_branches += _calculate_number_of_branches(morphology, child, node_types)
            break
    # we make it here when we're at a tip or when a bifurcation has
    #   been analyzed
    # if this isn't a soma node then it's time to increment branch count
    if root['type'] != SOMA:
        num_branches += 1
    return num_branches


def calculate_number_of_branches(morphology, root=None, node_types=None):

    """
        Calculate the number of branches. A branch is defined as one
        or more compartments that lie between bifurcations or between a
        bifurcation and a termination point.
        The soma is considered a bifurcation point, regardless of how many
        stems it has.

        Parameters
        ----------

        morphology: Morphology object

        root: dict
        This is the node from which to count branches under.
        When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value
    """
    num_branches = 0
    roots = morphology.get_roots_for_analysis(root, node_types)
    if roots is None:
        return float('nan')
    for node in roots:
        num_branches += _calculate_number_of_branches(morphology, node, node_types)
    return num_branches


def calculate_core_features(morphology, node_types):
    features = {}
    soma = morphology.get_root()
    features["max_path_distance"] = calculate_max_path_distance(morphology, node_types=node_types)
    features["num_bifurcations"] = calculate_number_of_bifurcations(morphology, node_types=node_types)
    features["num_outer_bifurcations"] = calculate_outer_bifs(morphology, soma, node_types)
    features["num_neurites"] = calculate_number_of_neurites(morphology, node_types=node_types)
    features["num_branches"] = calculate_number_of_branches(morphology, node_types=node_types)
    if features["num_branches"] != float('nan') and features["num_branches"] != 0:
        features["neurites_over_branches"] = 1.0 * features["num_branches"] / features["num_branches"]
    else:
        features["neurites_over_branches"] = float('nan')
    features["num_tips"] = calculate_number_of_tips(morphology, node_types=node_types)
    features["max_branch_order"] = calculate_max_branch_order(morphology, node_types=node_types)
    features["contraction"] = calculate_mean_contraction(morphology, node_types=node_types)
    features["num_nodes"] = len(morphology.get_node_by_types(node_types))
    features["total_length"] = calculate_total_length(morphology, node_types=node_types)
    features["mean_parent_daughter_ratio"] = calculate_mean_parent_daughter_ratio(morphology, node_types=node_types)
    features["mean_fragmentation"] = calculate_mean_fragmentation(morphology, node_types=node_types)
    features["bifurcation_angle_remote"] = calculate_bifurcation_angle_remote(morphology, node_types=node_types)
    features["bifurcation_angle_local"] = calculate_bifurcation_angle_local(morphology, node_types=node_types)
    features["parent_daughter_ratio"] = calculate_parent_daughter_ratio(morphology, node_types=node_types)
    features["average_diameter"] = calculate_mean_diameter(morphology, node_types=node_types)
    sfc, vol = calculate_total_size(morphology, node_types=node_types)
    features["total_surface"] = sfc
    features["total_volume"] = vol
    features["early_branch"] = calculate_early_branch_path(morphology, node_types=node_types, soma=soma)
    features["num_stems"] = calculate_number_of_stems_by_type(morphology, node_types)
    features["max_euclidean_distance"] = calculate_max_euclidean_distance(morphology, node_types)

    return features
