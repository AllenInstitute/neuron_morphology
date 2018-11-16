import numpy as np
import math
from allensdk.neuron_morphology.constants import *
import scipy.stats


def unit_vector(vector):

    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)


def angle_between(v1, v2):

    """ Returns the angle in radians between vectors 'v1' and 'v2'::

    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)

    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def _get_roots_for_analysis(morphology, root, node_types):

    """
        Returns a list of all trees to be analyzed, based on the supplied root.
        These trees are the list of all children of the root, if root is
        not None, and the root node of all trees in the morphology if root
        is None.

        Parameters
        ----------
        morphology: Tree object

        root: dict
        This is the node from which to count branches under. When root=None,
        all separate trees in the morphology are returned.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Array of Node objects

    """

    if root is None:
        # if root not specified, grab the soma root if it exists, and the
        #   root of the first disconnected tree if not
        nodes = morphology.get_node_by_types(node_types)

        roots = morphology.get_tree_roots_for_nodes(nodes)
    else:
        roots = morphology.get_children(root, node_types)
    return roots


def calculate_max_euclidean_distance(morphology, node_types):

    """
        Calculate the furthest distance, in 3-space, of a
        compartment's end from the soma.
        This is equivalent to the distance to the furthest SWC node.

        Parameters
        ----------

        morphology: Tree object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    soma = morphology.get_root()
    nodes = morphology.get_node_by_types(node_types)

    distances = []
    for node in nodes:
        distances.append(morphology.euclidean_distance(soma, node))

    return max(distances)


def calculate_number_of_stems(morphology):

    """
        Calculate the number of soma stems.
        This is defined as the total number of non-soma child nodes on soma nodes.

        Parameters
        ----------

        morphology: Tree object

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
        morphology: Tree object

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

        morphology: Tree object

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


def calculate_dimensions(morphology, node_types):

    """
        Measures overall size on each dimension: width(x), height(z) and depth(z).
        Soma nodes are not included in this measurement.

        Parameters
        ----------

        morphology: Tree object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        3-element array: [width, height, depth]

    """

    return morphology.get_dimensions(node_types)


def calculate_total_length(morphology, node_types):

    """
        Calculate the total length of all segments in the morphology

        Parameters
        ----------

        morphology: Tree object

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
    compartment_list = morphology.get_compartment_list(nodes)
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

        nodes: Tree object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    nodes = morphology.get_node_by_types(node_types)

    return len(nodes)


def calculate_soma_surface(morphology):

    """
        Approximates the surface area of the soma. Morphologies with only
        a single soma node are supported.

        Parameters
        ----------
        morphology: Tree object

        Returns
        -------

        Scalar value

    """

    soma = morphology.get_root()
    return 4.0 * math.pi * soma['radius'] * soma['radius']


def calculate_mean_diameter(morphology, node_types):

    """
        Calculates the average diameter of all non-soma nodes.

        Parameters
        ----------

        morphology: Tree object

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
        morphology: Tree object

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


def calculate_centroid(morphology, soma, nodes):

    """
        Calculates first moments of all bifurcating compartments
        (compartments with 2 or more children) along each axis

        Parameters
        ----------

        morphology: Tree object

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

        morphology: Tree object

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

        morphology: Tree object

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


def calculate_skewness(values_x, values_y, values_z):

    #########################
    # calculate third moment (skewness)
    # from wikipedia:
    #   skew = E[((X-mean)/stdev)^3]
    # where E[x] is the mean of all values x
    # NOTE: scipy eliminates ability to weigh compartments by length,
    #   so result will be biased by segmentation strategy

    skew = np.zeros(3)
    skew[0] = scipy.stats.skew(np.asarray(values_x))
    skew[1] = scipy.stats.skew(np.asarray(values_y))
    skew[2] = scipy.stats.skew(np.asarray(values_z))
    return skew


def calculate_kurtosis(values_x, values_y, values_z):

    kurtosis = np.zeros(3)
    kurtosis[0] = scipy.stats.kurtosis(values_x)
    kurtosis[1] = scipy.stats.kurtosis(values_y)
    kurtosis[2] = scipy.stats.kurtosis(values_z)
    return kurtosis


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


def calculate_compartment_moments(morphology, soma, node_types):

    """
        Calculates first and second moments of all compartments along each axis

        Parameters
        ----------

        morphology: Tree object

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
    compartment_list = morphology.get_compartment_list(nodes)
    values_x, values_y, values_z = calculate_values_for_compartments(morphology, soma, compartment_list)
    centroid = calculate_centroid_for_compartments(morphology, soma, compartment_list)
    second = calculate_second_for_compartments(morphology, soma, centroid, compartment_list)
    skew = calculate_skewness(values_x, values_y, values_z)
    kurtosis = calculate_kurtosis(values_x, values_y, values_z)
    return centroid, second, skew, kurtosis


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

        morphology: Tree object

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


def calculate_mean_parent_daughter_ratio(morphology, node_types):

    """
        Returns the average ratio of child diameter to parent diameter.

        Parameters
        ----------

        morphology: Tree object

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

        morphology: Tree object

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

        morphology: Tree object

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


def calculate_total_size(morphology, node_types):

    """
        Calculates the total surface area and volume of non-soma compartments.

        Parameters
        ----------

        morphology: Tree object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Two scalar values: total surface, total volume

    """
    total_sfc = 0.0
    total_vol = 0.0
    nodes = morphology.get_node_by_types(node_types)
    compartments = morphology.get_compartment_list(nodes)
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


def calculate_outer_bifs(morphology, soma, node_types):

    """
        Counts the number of bifurcation points beyond the a sphere
        with 1/2 the radius from the soma to the most distant point
        in the morphology, with that sphere centered at the soma.

        Parameters
        ----------

        morphology: Tree object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        int: the number of bifurcations

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


def calculate_bifurcation_angle_remote(morphology, node_types):

    """
        Compute the average angle between the next branch point or terminal
        tip of child segments at each bifurcation.
        Trifurcations are ignored. Note: this introduces possible segmentation
        artifacts if trifurcations are due to large segment sizes.

        Parameters
        ----------

        morphology: Tree object

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

        morphology: Tree object

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

        morphology: Tree object

        root: dict
        This is the node from which to count branches under.
        When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    roots = _get_roots_for_analysis(morphology, root, node_types)
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

        morphology: Tree object

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
    roots = _get_roots_for_analysis(morphology, root, node_types)
    if roots is None:
        return float('nan')
    for node in roots:
        order = _calculate_max_branch_order(morphology, node, node_types)
        if order > max_order:
            max_order = order
    return max_order


def _calculate_mean_contraction(morphology, reference, root, node_types):

    """
        Calculate the average contraction of all sections. In other words,
        calculate the average ratio of euclidean distance to path distance
        between all bifurcations in the morphology. Trifurcations are treated
        as bifurcations.

        Parameters
        ----------

        morphology: Tree object

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

    """
        Calculate the average contraction of all sections. In other words,
        calculate the average ratio of euclidean distance to path distance
        between all bifurcations in the morphology. Trifurcations are treated
        as bifurcations.

        Parameters
        ----------

        morphology: Tree object

        root: dict
        This is the node from which to measure branche contraction under.
        When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """
    roots = _get_roots_for_analysis(morphology, root, node_types)
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


def _calculate_number_of_branches(morphology, root, node_types):

    """
        Calculate the number of branches. A branch is defined as one
        or more compartments that lie between bifurcations or between a
        bifurcation and a termination point.
        The soma is considered a bifurcation point, regardless of how many
        stems it has.

        Parameters
        ----------

        morphology: Tree object

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

        morphology: Tree object

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
    roots = _get_roots_for_analysis(morphology, root, node_types)
    if roots is None:
        return float('nan')
    for node in roots:
        num_branches += _calculate_number_of_branches(morphology, node, node_types)
    return num_branches


def _calculate_max_path_distance(morphology, root, node_types):
    # if root not specified, grab the soma root if it exists, and the
    #   root of the first disconnected tree if not
    nodes = morphology.get_node_by_types(node_types)
    if morphology.get_number_of_trees(nodes) == 0:
        return float('nan')
    if root is None:
        root = morphology.get_root()
    total_length = 0.0
    # sum up length for all child compartments
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
            if root['type'] != SOMA and root['type'] in node_types:
                compartment = morphology.get_compartment_for_node(root, nodes)
                if compartment:
                    total_length += morphology.get_compartment_length(compartment)
            root = morphology.get_children(root)[0]
        else:
            # we reached a bifurcation point
            # recurse to find length of each child branch and then
            #   exit loop
            max_sub_dist = 0.0
            children_of_root = morphology.get_children(root, node_types)
            for child in children_of_root:
                dist = _calculate_max_path_distance(morphology, child, node_types)
                if dist > max_sub_dist:
                    max_sub_dist = dist
            total_length += max_sub_dist
            break
    # the length of this compartment hasn't been included yet, and if it
    #   isn't part of the soma
    if root['type'] != SOMA:
        compartment = morphology.get_compartment_for_node(root, nodes)
        if compartment:
            total_length += morphology.get_compartment_length(compartment)
    return total_length


def calculate_max_path_distance(morphology, root=None, node_types=None):

    """
        Calculate the distance, following the path of adjacent
        neutrites, from the soma to the furthest compartment.
        This is equivalent to the distance to the furthest SWC node.

        Parameters
        ----------

        morphology: Tree object

        root: dict
        This is the root node from which to calculate the max path
        length. When root=None, the soma is used.

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    max_path = 0.0
    roots = _get_roots_for_analysis(morphology, root, node_types)
    if roots is None:
        return float('nan')
    for node in roots:
        path = _calculate_max_path_distance(morphology, node, node_types)
        if path > max_path:
            max_path = path
    return max_path


def calculate_early_branch_path(morphology, soma, node_types=None):

    """
        Returns the ratio of the longest 'short' branch from a
        bifurcation to the maximum path length of the tree. In other
        words, for each bifurcation, the maximum path length below that
        branch is calculated, and the shorter of these values is used.
        The maximum of these short values is divided by the maximum
        path length.

        Parameters
        ----------

        morphology: Tree object

        soma: dict
        soma node

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        float: ratio of max short branch to max path length

    """
    longest_short = 0.0
    path_len = _calculate_max_path_distance(morphology, soma, node_types)
    nodes = morphology.get_node_by_types(node_types)
    if path_len == 0:
        return 0.0
    for node in nodes:
        if len(morphology.get_children(node, node_types)) < 2:
            continue
        a = _calculate_max_path_distance(morphology, morphology.children_of(node)[0], node_types)
        b = _calculate_max_path_distance(morphology, morphology.children_of(node)[1], node_types)
        longest_short = max(longest_short, min(a, b))
    return 1.0 * longest_short / path_len
