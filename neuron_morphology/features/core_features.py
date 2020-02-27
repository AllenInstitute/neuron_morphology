import math
from importlib import import_module

from allensdk.deprecated import deprecated

from neuron_morphology.constants import *
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
