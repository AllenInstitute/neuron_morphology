import numpy as np
import math
import sys
from .. import swc
from .. import node
import scipy.stats
#from .. import node.euclidean_distance as euclidean_distance
#import ..node
#from .. import morphology Morphology

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / np.linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0))


def _get_roots_for_analysis(morph, root):
    """
    Returns a list of all trees to be analyzed, based on the supplied root.
    These trees are the list of all children of the root, if root is 
    not None, and the root node of all trees in the morphology if root 
    is None.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under. When root=None,
    all separate trees in the morphology are returned.

    Returns
    -------
    Array of Node objects

    """
    if root is None:
        if morph.num_trees == 0:
            return None
        # if root not specified, grab the soma root if it exists, and the 
        #   root of the first disconnected tree if not
        roots = []
        for i in range(morph.num_trees):
            roots.append(morph.node(morph.tree(i)[0]))
    else:
        roots = []
        for node_id in root.children:
            roots.append(morph.node(node_id))
    return roots

########################################################################

def calculate_compartment_moments(morph, soma):
    """ Calculates first and second moments of all compartments along each
    axis
    
    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Two 3-element arrays. The first is the first moments on X,Y,Z. The
    second is the second moments on X,Y,Z. 
    """
    # IT-14207: calculations previously generated centroid in absolute
    #   measure. features need this to be relative to the soma
    # calculate first moment (centroid) along each axis
    centroid = np.zeros(3)
    norm = 0
    n = 0
    for comp in morph.compartment_list:
        if comp.node2.t == 1:   # ignore soma compartments in this calculation
            continue
        # make centroid relative to soma
        centroid[0] += (comp.center[0] - soma.x) * comp.length
        centroid[1] += (comp.center[1] - soma.y) * comp.length
        centroid[2] += (comp.center[2] - soma.z) * comp.length
        norm += comp.length
        n += 1
    # if no compartments, return null
    if norm == 0:
        empty = [float('nan'), float('nan'), float('nan')]
        return empty, empty, empty, empty
    # to get centroid we must divide by average compartment length and by
    #   number of compartments. this simplifies to being divided by
    #   summed compartment length. ie, centroid /= (norm/len) * len
    centroid /= 1.0 * (norm/n) * n
    #########################
    # calculate second moment
    second = np.zeros(3)
    for comp in morph.compartment_list:
        if comp.node2.t == 1:   # ignore soma compartments in this calculation
            continue
        dist = (soma.x + centroid[0]) - comp.center[0]
        #second[0] += dist * dist 
        second[0] += dist * dist * comp.length
        #
        dist = (soma.y + centroid[1]) - comp.center[1]
        #second[1] += dist * dist 
        second[1] += dist * dist * comp.length
        #
        dist = (soma.z + centroid[2]) - comp.center[2]
        #second[2] += dist * dist 
        second[2] += dist * dist * comp.length
    second /= 1.0 * (norm/n) * n
    #########################
    # calculate third moment (skewness)
    # from wikipedia:
    #   skew = E[((X-mean)/stdev)^3]
    # where E[x] is the mean of all values x
    # implementation not working properly. moving to scipy version.
    # NOTE: scipy eliminates ability to weigh compartments by length,
    #   so result will be biased by segmentation strategy
    vals_x = []
    vals_y = []
    vals_z = []
    for comp in morph.compartment_list:
        if comp.node2.t == 1:   # ignore soma compartments in this calculation
            continue
        vals_x.append(comp.center[0] - soma.x)
        vals_y.append(comp.center[1] - soma.y)
        vals_z.append(comp.center[2] - soma.z)
    skew = np.zeros(3)
    skew[0] = scipy.stats.skew(vals_x)
    skew[1] = scipy.stats.skew(vals_y)
    skew[2] = scipy.stats.skew(vals_z)
    kurt = np.zeros(3)
    kurt[0] = scipy.stats.kurtosis(vals_x)
    kurt[1] = scipy.stats.kurtosis(vals_y)
    kurt[2] = scipy.stats.kurtosis(vals_z)
    # morphology only assumed to be oriented along Y axis, so make X,Z axes
    #   unsigned
    centroid[0] = abs(centroid[0])
    centroid[2] = abs(centroid[2])
    return centroid, second, skew, kurt

########################################################################

def calculate_bifurcation_moments(morph, soma):
    """ Calculates first and second moments of all bifurcating compartments 
    (compartments with 2 or more children) along each axis
    
    Parameters
    ----------
    morph: Morphology object

    node_type: enum
    Limit search to 

    Returns
    -------
    Two 3-element arrays. The first is the first moments on X,Y,Z. The
    second is the second moments on X,Y,Z. "None, None" is returned if
    the compartment list is empty
    """
    # calculate first moment (centroid) along each axis
    centroid = np.zeros(3)
    n = 0
    for node in morph.node_list:
        if node.t == 1:   # ignore soma compartments in this calculation
            continue
        if len(node.children) > 1:
            centroid[0] += node.x - soma.x
            centroid[1] += node.y - soma.y
            centroid[2] += node.z - soma.z
            n += 1
    # if no compartments, return null
    if n == 0:
        empty = [float('nan'), float('nan'), float('nan')]
        return empty, empty, empty, empty
    centroid /= 1.0 * n
    #########################
    # calculate second moment
    second = np.zeros(3)
    for node in morph.node_list:
        if node.t == 1:   # ignore soma compartments in this calculation
            continue
        if len(node.children) > 1:
            # x
            dist = (centroid[0] + soma.x) - node.x
            second[0] += dist * dist
            # y
            dist = (centroid[1] + soma.y) - node.y
            second[1] += dist * dist
            # z
            dist = (centroid[2] + soma.z) - node.z
            second[2] += dist * dist
    second /= 1.0 * n
    #########################
    # calculate third moment (skewness)
    # from wikipedia:
    #   skew = E[((X-mean)/stdev)^3]
    # where E[x] is the mean of all values x
    # NOTE: scipy eliminates ability to weigh compartments by length,
    #   so result will be biased by segmentation strategy
    vals_x = []
    vals_y = []
    vals_z = []
    for node in morph.node_list:
        if node.t == 1:   # ignore soma compartments in this calculation
            continue
        if len(node.children) > 1:
            vals_x.append(node.x - soma.x)
            vals_y.append(node.y - soma.y)
            vals_z.append(node.z - soma.z)
    skew = np.zeros(3)
    skew[0] = scipy.stats.skew(vals_x)
    skew[1] = scipy.stats.skew(vals_y)
    skew[2] = scipy.stats.skew(vals_z)
    kurt = np.zeros(3)
    kurt[0] = scipy.stats.kurtosis(vals_x)
    kurt[1] = scipy.stats.kurtosis(vals_y)
    kurt[2] = scipy.stats.kurtosis(vals_z)
    # morphology only assumed to be oriented along Y axis, so make X,Z axes
    #   unsigned
    centroid[0] = abs(centroid[0])
    centroid[2] = abs(centroid[2])
    return centroid, second, skew, kurt

########################################################################

def calculate_max_euclidean_distance(morph, node_type=None):
    """ Calculate the furthest distance, in 3-space, of a 
    compartment's end from the soma.
    This is equivalant to the distanc to the furthest SWC node.

    Parameters
    ----------
    morph: Morphology object

    node_type: enum (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
    Type to restrict search to

    Returns
    -------
    Scalar value
    """
    soma = morph.soma_root()
    if soma is None:
        return float('nan')
    max_dist = 0.0
    for node in morph.node_list:
        if node_type is not None and node.t != node_type:
            continue
        # use compartment's node2, which is the tip end of the compartment.
        # this omits root nodes from the calculation, but that's OK in all
        #   cases except a disconnected tree whose root is further from
        #   the soma than any other node. this is OK because feature analyses 
        #   don't work well with disconnected trees, and the expected error
        #   in such an edge case is very small
        dx = soma.x - node.x
        dy = soma.y - node.y
        dz = soma.z - node.z
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)
        if dist > max_dist:
            max_dist = dist
    return max_dist
    
########################################################################

def _calculate_max_path_distance(morph, root):
    # if root not specified, grab the soma root if it exists, and the 
    #   root of the first disconnected tree if not
    if morph.num_trees == 0:
        return float('nan')
    if root is None:
        root = morph.node(morph.tree(0)[0])
    total_length = 0.0
    # sum up length for all child compartments
    while len(root.children) > 0:
        # the next node is a continuation from this node (ie, no 
        #   bifurcation). update path length and evaluate the
        #   next node
        # path tracing is done using nodes. if a node is associated
        #   with a compartment (all non-root nodes are) then add that
        #   compartment's length to the accumulated distance
        if len(root.children) == 1:
            # get length of associated compartment, if it exists, and if
            #   it's not soma
            if root.compartment_id >= 0 and root.t != 1:
                comp = morph.compartment(root.compartment_id)
                total_length += comp.length
            root = morph.node(root.children[0])
        else:
            # we reached a bifurcation point
            # recurse to find length of each child branch and then
            #   exit loop
            max_sub_dist = 0.0
            for child_id in root.children:
                child = morph.node(child_id)
                dist = _calculate_max_path_distance(morph, child)
                if dist > max_sub_dist:
                    max_sub_dist = dist
            total_length += max_sub_dist
            break
    # the length of this compartment hasn't been included yet, and if it
    #   isn't part of the soma
    if root.t != 1 and root.compartment_id >= 0:
        comp = morph.compartment(root.compartment_id)
        total_length += comp.length
    return total_length


def calculate_max_path_distance(morph, root=None):
    """ Calculate the distance, following the path of adjacent
    neurites, from the soma to the furthest compartment.
    This is equivalant to the distanc to the furthest SWC node.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the root node from which to calculate the max path
    length. When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    max_path = 0.0
    roots = _get_roots_for_analysis(morph, root)
    if roots is None:
        return float('nan')
    for node in roots:
        path = _calculate_max_path_distance(morph, node)
        if path > max_path:
            max_path = path
    return max_path


########################################################################

def calculate_num_stems(morph):
    """ Calculate the number of soma stems. 
    This is defined as the total number of non-soma child nodes on soma nodes. 

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    stems = 0
    for comp in morph.compartment_list:
        if comp.node1.t == 1 and comp.node2.t != 1:
            stems += 1
    return stems

########################################################################

def calculate_num_stems_by_type(morph, node_type):
    """ Calculate the number of soma stems. 
    This is defined as the total number of non-soma child nodes on soma nodes. 

    Parameters
    ----------
    morph: Morphology object

    node_type: enum (SWC node type: ie, 2, 3 or 4)

    Returns
    -------
    Scalar value
    """
    stems = 0
    for comp in morph.compartment_list:
        if comp.node1.t == 1 and comp.node2.t == node_type:
            stems += 1
    return stems

########################################################################

# TODO deprecate in favor of calculate_num_branches()
def calculate_num_bifurcations(morph):
    """ Calculates the number of bifurcating nodes in the morphology.
    A bifurcation is defined as a non-soma node having 2 child nodes.
    A non-soma node having more than 2 children is ... FIXME -- FINISH DEFN

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    if morph.num_trees == 0:
        return float('nan')
    bifs = 0
    for comp in morph.compartment_list:
        if comp.node2.t != 1:
            if len(comp.node2.children) == 2:
                bifs += 1
            elif len(comp.node2.children) > 2:
                bifs += len(comp.node2.children) - 1
    return bifs

########################################################################

def _calculate_num_branches(morph, root):
    """ Calculate the number of branches. A branch is defined as one
    or more compartments that lie between bifurcations or between a 
    bifurcation and a termination point.
    The soma is considered a bifurcation point, regardless of how many
    stems it has.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    # advance to next bifurcation or tip and increment counter
    # on bifurcation, recurse into this function again
    # treat trifurcation as 2 successive bifs
    num_branches = 0
    while len(root.children) > 0:
        # if the next compartment is a continuation (ie, no 
        #   bifurcation) then get the next node
        if len(root.children) == 1:
            root = morph.node(root.children[0])
        else:
            if root.t != 1 and len(root.children) > 2:
                # treat trifurcation as successive bifs and increment
                #   branch counter to acknowledge implicit branch
                num_branches += len(root.children) - 2
            # we reached a bifurcation point
            # recurse to find the number of branches along each path
            #   exit loop
            for child_id in root.children:
                child = morph.node(child_id)
                num_branches += _calculate_num_branches(morph, child)
            break
    # we make it here when we're at a tip or when a bifurcation has
    #   been analyzed
    # if this isn't a soma node then it's time to increment branch count
    if root.t != 1:
        num_branches += 1
    return num_branches

def calculate_num_branches(morph, root=None):
    """ Calculate the number of branches. A branch is defined as one
    or more compartments that lie between bifurcations or between a 
    bifurcation and a termination point.
    The soma is considered a bifurcation point, regardless of how many
    stems it has.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    num_branches = 0
    roots = _get_roots_for_analysis(morph, root)
    if roots is None:
        return float('nan')
    for node in roots:
        num_branches += _calculate_num_branches(morph, node)
    return num_branches

########################################################################

def calculate_num_tips(morph):
    """ Counts the number of endpoints (ie, non-soma nodes that have
    no children)

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    if morph.num_trees == 0:
        return float('nan')
    tips = 0
    for node in morph.node_list:
        if node.t != 1 and len(node.children) == 0:
            tips += 1
    return tips

########################################################################

def calculate_dimensions(morph):
    """ Measures overall size on each dimension: width(x), height(z) and
    depth(z). Soma nodes are not included in this measurement.

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    3-element array: [width, height, depth]
    """
    # we can't assume the soma is at the root -- e.g., we could be
    #   measuring a morphology that consists only of disconnected 
    #   axon segments. however, we do need something to base initial
    #   min/max values on
    if morph.num_trees == 0:
        return [float('nan'), float('nan'), float('nan')]
    root = morph.node(morph.tree(0)[0])
    x_min = root.x
    x_max = root.x
    y_min = root.y
    y_max = root.y
    z_min = root.z
    z_max = root.z
    for node in morph.node_list:
        if node.t != 1:
            if node.x < x_min:
                x_min = node.x
            if node.x > x_max:
                x_max = node.x
            if node.y < y_min:
                y_min = node.y
            if node.y > y_max:
                y_max = node.y
            if node.z < z_min:
                z_min = node.z
            if node.z > z_max:
                z_max = node.z
    return [x_max-x_min, y_max-y_min, z_max-z_min]

########################################################################

def _calculate_max_branch_order(morph, root):
    # advance to next bifurcation or tip and increment counter
    # on bifurcation, recurse into this function again
    # treat trifurcation as 2 successive bifs
    num_branches = 0
    while len(root.children) > 0:
        # if the next compartment is a continuation (ie, no 
        #   bifurcation) then get the next node
        if len(root.children) == 1:
            root = morph.node(root.children[0])
        elif len(root.children) > 1:
            # if this isn't a soma node then it's time to increment branch count
            if root.t != 1:
                num_branches += 1
            # we reached a bifurcation point
            # recurse to find the number of branches along each path
            #   exit loop
            max_depth = 0
            for child_id in root.children:
                child = morph.node(child_id)
                branches = _calculate_max_branch_order(morph, child)
                if branches > max_depth:
                    max_depth = branches
            num_branches += max_depth
            break
    return num_branches

def calculate_max_branch_order(morph, root=None):
    """ Calculate the maximum number of branches that exist between
    the root and the furthest (deepest) tip.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    max_order = 0
    roots = _get_roots_for_analysis(morph, root)
    if roots is None:
        return float('nan')
    for node in roots:
        order = _calculate_max_branch_order(morph, node)
        if order > max_order:
            max_order = order
    return max_order


########################################################################

def _calculate_mean_contraction(morph, reference, root):
    """ Calculate the average contraction of all sections. In other words,
    calculate the average ratio of euclidean distance to path distance
    between all bifurcations in the morphology. Trifurcations are treated
    as bifurcations.

    Parameters
    ----------
    morph: Morphology object

    reference: Node object
    This is the node of the previous bifurcation

    root: Node object
    This is the node from which to measure branch contraction under

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
    path_dist = node.euclidean_distance(reference, root)
    tot_path = 0.0
    tot_euc = 0.0
    while len(root.children) > 0:
        # if the next compartment is a continuation (ie, no 
        #   bifurcation) then get the next node
        if len(root.children) == 1:
            next_node = morph.node(root.children[0])
            path_dist += node.euclidean_distance(root, next_node)
            root = next_node
        else:
            # we reached a bifurcation point. recurse and analyze children
            for child_id in root.children:
                child = morph.node(child_id)
                euc, path = _calculate_mean_contraction(morph, root, child)
                tot_euc += euc
                tot_path += path
            break
    euc_dist += node.euclidean_distance(root, reference)
    return tot_euc + euc_dist, tot_path + path_dist

def calculate_mean_contraction(morph, root=None):
    """ Calculate the average contraction of all sections. In other words,
    calculate the average ratio of euclidean distance to path distance
    between all bifurcations in the morphology. Trifurcations are treated
    as bifurcations.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to measure branche contraction under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    roots = _get_roots_for_analysis(morph, root)
    if roots is None:
        return float('nan')
    euc_dist = 0.0
    path_dist = 0.0
    for node_id in roots:
        ref = morph.node(node_id)
        # advance to next bifurcation
        while len(ref.children) == 1:
            ref = morph.node(ref.children[0])
        if len(ref.children) == 0:
            continue
        # analyze each branch from this bifurcation point
        for child_id in ref.children:
            child = morph.node(child_id)
            euc, path = _calculate_mean_contraction(morph, ref, child)
            euc_dist += euc
            path_dist += path
    if path_dist == 0.0:
        return float('nan')
    return 1.0 * euc_dist / path_dist

########################################################################

def calculate_total_length(morph):
    """ Calculate the total length of all segments in the morphology

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    total_length = 0.0
    # sum the length of all compartments, excluding the case where the
    #   parent node is the soma root, as that compartment should heavily
    #   overlap the soma. Include non-soma-root parents, as those will
    #   be assumed to be on (at least nearer) the soma surface
    for comp in morph.compartment_list:
        if comp.node1.t == 1 and comp.node1.parent < 0:
            continue
        total_length += comp.length
    return total_length

########################################################################

def calculate_num_neurites(morph):
    """ Returns the number of non-soma compartments in the morphology

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    n = 0
    for comp in morph.compartment_list:
        if comp.node2.t != 1:
            n += 1
    return n

########################################################################

def calculate_mean_parent_daughter_ratio(morph):
    """ Returns the average ratio of child diameter to parent diameter.

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    total = 0.0
    cnt = 0.0
    try:
        for node in morph.node_list:
            if node.t == 1 or len(node.children) < 2:
                continue
            child_radii = 0.0
            for child_id in node.children:
                child = morph.node(child_id)
                child_radii += child.radius
            child_radii /= 1.0 * len(node.children)
            total += child_radii / node.radius
            cnt += 1.0
    except ZeroDivisionError:
        # node radius was zero?
        cnt = 0
    if cnt == 0:
        return float('nan')
    return total / cnt

########################################################################

def _calculate_mean_fragmentation(morph, root, initial_seg=False):
    """ Compute the average number of compartments between successive
    branch points. Trifurcations are treated as bifurcations.
    NOTE: this feature is directly dependent on segmentation policy
    and will likely change whenever a morphology is resegmented.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branch contraction under.

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
        if len(root.children) >= 2:
            # we reached a bifurcation point
            # recurse to find the number of branches along each path
            #   exit loop
            if not initial_seg:
                local_comparts += 1
                if local_branches == 0:
                    local_branches = 1
            for child_id in root.children:
                child = morph.node(child_id)
                if root.t == 1:
                    initial = True
                else:
                    initial = False
                branches, cnt = _calculate_mean_fragmentation(morph, child, initial)
                child_branches += branches
                child_comparts += cnt
            break
        else:
            if not initial_seg:
                local_comparts += 1
                if local_branches == 0:
                    local_branches = 1
            if len(root.children) == 0:
                break
            root = morph.node(root.children[0])
    # we make it here when we're at a tip or when a bifurcation has
    #   been analyzed
    return local_branches + child_branches, local_comparts + child_comparts


def calculate_mean_fragmentation(morph, root=None):
    """ Compute the average number of compartments between successive
    branch points and between branch points and tips. 
    Trifurcations are treated as bifurcations.
    NOTE: This feature is directly dependent on segmentation policy
    and will likely change whenever a morphology is resegmented.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    roots = _get_roots_for_analysis(morph, root)
    if roots is None:
        return float('nan')
    n_branches = 0.0
    n_compartments = 0.0
    for node in roots:
        br, comp = _calculate_mean_fragmentation(morph, node, True)
        n_branches += br
        n_compartments += comp
    if n_branches == 0.0:
        return float('nan')
    return 1.0 * n_compartments / n_branches

########################################################################

def calculate_bifurcation_angle_local(morph, root=None):
    """ Compute the average angle between child segments at
    bifurcations throughout the morphology. 
    Trifurcations are ignored. Note: this introduces possible segmentation
    artifacts if trifurcations are due to large segment sizes.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    if root is None:
        if morph.num_trees == 0:
            return float('nan')
        # if root not specified, grab the soma root if it exists, and the 
        #   root of the first disconnected tree if not
        root = morph.node(morph.tree(0)[0])
    angle = 0.0
    n = 0.0
    try:
        for node in morph.node_list:
            if node.t == 1:
                continue
            if len(node.children) == 2:
                a = morph.node(node.children[0])
                ax = a.x - node.x
                ay = a.y - node.y
                az = a.z - node.z
                b = morph.node(node.children[1])
                bx = b.x - node.x
                by = b.y - node.y
                bz = b.z - node.z
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

########################################################################

def calculate_bifurcation_angle_remote(morph, root=None):
    """ Compute the average angle between the next branch point or terminal
    tip of child segments at each bifurcation.
    Trifurcations are ignored. Note: this introduces possible segmentation
    artifacts if trifurcations are due to large segment sizes.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to count branches under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    if root is None:
        if morph.num_trees == 0:
            return float('nan')
        # if root not specified, grab the soma root if it exists, and the 
        #   root of the first disconnected tree if not
        root = morph.node(morph.tree(0)[0])
    angle = 0.0
    n = 0.0
    for node in morph.node_list:
        if node.t == 1:
            continue
        if len(node.children) == 2:
            # find the point to measure to, whether it be the next
            #   branch point or tip
            a = morph.node(node.children[0])
            while len(a.children) == 1:
                a = morph.node(a.children[0])
            ax = a.x - node.x
            ay = a.y - node.y
            az = a.z - node.z
            b = morph.node(node.children[1])
            while len(b.children) == 1:
                b = morph.node(b.children[0])
            bx = b.x - node.x
            by = b.y - node.y
            bz = b.z - node.z
            dot = ax*bx + ay*by + az*bz
            len_a = math.sqrt(ax*ax + ay*ay + az*az)
            len_b = math.sqrt(bx*bx + by*by + bz*bz)
            theta = 180.0 * math.acos(dot / (len_a * len_b)) / math.pi
            angle += theta
            n += 1.0
    if n == 0.0:
        return float('nan')
    return 1.0 * angle / n

########################################################################

# TODO deprecate as duplicate calculate_mean_parent_daughter_ratio()
def calculate_parent_daughter_ratio(morph, root=None):
    """ Compute the average ratio of parent node to daughter node at
    each branch point.

    Parameters
    ----------
    morph: Morphology object

    root: Node object
    This is the node from which to analyze parent-daughter ratio under.
    When root=None, the soma is used.

    Returns
    -------
    Scalar value
    """
    if root is None:
        if morph.num_trees == 0:
            return float('nan')
        # if root not specified, grab the soma root if it exists, and the 
        #   root of the first disconnected tree if not
        root = morph.node(morph.tree(0)[0])
    ratio_sum = 0.0
    n = 0
    try:
        for parent in morph.node_list:
            if parent.t == 1:
                continue
            if len(parent.children) > 1:
                for child_id in parent.children:
                    daughter = morph.node(child_id)
                    ratio = daughter.radius / parent.radius
                    ratio_sum += ratio
                    n += 1
    except ZeroDivisionError:
        n = 0   # node radius is zero. uncomputable
    if n == 0:
        return float('nan')
    return 1.0 * ratio_sum / n

########################################################################

def calculate_soma_surface(morph):
    """ Approximates the surface area of the soma. Morphologies with only
    a single soma node are supported.

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    soma = morph.soma_root()
    if soma is None:
        return float('nan')
    # count how many soma nodes
    tree = morph.tree(0)
    cnt = 0
    for node_id in tree:
        if morph.node(node_id).t == 1:
            cnt += 1
    if cnt > 1:
        print("Unable to calculate soma size when more than one soma compartment is present")
        return float('nan')
    return 4.0 * math.pi * soma.radius * soma.radius

########################################################################

def calculate_mean_diameter(morph):
    """ Calculates the average diameter of all non-soma nodes.

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Scalar value
    """
    total = 0.0
    n = 0
    for node in morph.node_list:
        if node.t == 1:
            continue
        total += 2.0 * node.radius
        n += 1
    if n == 0:
        return float('nan')
    return 1.0 * total / n

########################################################################

def calculate_total_size(morph):
    """ Calculates the total surface area and volume of non-soma compartments.

    Parameters
    ----------
    morph: Morphology object

    Returns
    -------
    Two scalar values: total surface, total volume
    """
    total_sfc = 0.0
    total_vol = 0.0
    for comp in morph.compartment_list:
        if comp.node1.t == 1:
            continue
        r1 = comp.node1.radius
        r2 = comp.node2.radius
        total_sfc += 2.0 * math.pi * (0.5 * (r1 + r2)) * comp.length
        # vol = sigma(0,L) pi * r^2 * dx
        # DR = r2 - r1
        # r = f(x) = r1 + x/L * DR
        # vol = pi * sigma(0,L) (r1 + x/L * DR)^2 * dx
        # vol = pi * sigma(0,L) (r1^2 + 2x/L*DR + x^2/L^2*DR^2) * dx
        # vol = pi * (x*r1^2 + x^2/L*DR + 1/3 * x^3/L^2*DR^2) | 0,L
        # vol = pi * ((L*r1^2 + L^2/L*DR + 1/3 * L^3/L^2*DR^2) - 0)
        # vol = pi * (L*r1^2 + L*DR + L/3*DR^2)
        DR = r2 - r1
        L = comp.length
        vol = math.pi * (L*r1*r1 + L*DR  + L*DR*DR/3.0)
        total_vol += vol
    return total_sfc, total_vol


########################################################################

def calculate_outer_bifs(morph, soma, t=None):
    """ Counts the number of bifurcation points beyond the a sphere
        with 1/2 the radius from the soma to the most distant point
        in the morphology, with that sphere centered at the soma.

        Parameters
        ----------
        morph: Morphology object

        t: int
        SWC type to analyze, or None to count from all types

        Returns
        -------
        int: the number of bifurcations
    """
    far = 0
    for node in morph.node_list:
        if t is not None and node.t != t:
            continue
        dist = node.euclidean_distance(soma, node)
        if dist > far:
            far = dist
    count = 0
    rad = far / 2.0
    for node in morph.node_list:
        if t is not None and node.t != t:
            continue
        if len(node.children) > 1:
            dist = node.euclidean_distance(soma, node)
            if dist > rad:
                count += 1
    return count


########################################################################

def calculate_early_branch_path(morph, soma):
    """ Returns the ratio of the longest 'short' branch from a 
        bifurcation to the maximum path length of the tree. In other 
        words, for each bifurcation, the maximum path length below that
        branch is calculated, and the shorter of these values is used. 
        The maximum of these short values is divided by the maximum 
        path length.

        Parameters
        ----------
        morph: Morphology object

        Returns
        -------
        float: ratio of max short branch to max path length
    """
    longest_short = 0.0
    path_len = _calculate_max_path_distance(morph, soma)
    if path_len == 0:
        return 0.0
    for node in morph.node_list:
        if len(node.children) < 2:
            continue
        a = _calculate_max_path_distance(morph, morph.node(node.children[0]))
        b = _calculate_max_path_distance(morph, morph.node(node.children[1]))
        longest_short = max(longest_short, min(a, b))
    return 1.0 * longest_short / path_len


########################################################################

def calculate_axon_base(morph, soma):
    """ AXON-ONLY feature.
        Returns the relative radial position on the soma where the
        tree holding the axon connects to the soma. 0 is on the bottom,
        1 on the top, and 0.5 out a side.
        Also returns the distance between the axon root and the soma
        surface (0 if axon connects to soma, >0 if axon branches from
        dendrite).

        Parameters
        ----------
        morph: Morphology object

        Returns
        -------
        (float, float):
        First value is relative position (height, on [0,1]) of axon 
            tree on soma. Second value is distance of axon root from
            soma
    """
    # find axon node, get it's tree ID, fetch that tree, and see where
    #   it connects to the soma radially
    tree_root = None
    dist = 0
    for node in morph.tree(0):
        if node.t == 2:
            prev_node = node
            # trace back to soma, to get stem root
            while morph.node(node.parent).t != 1:
                node = morph.node(node.parent)
                if node.parent == -1:
                    raise Exception("SWC error -- no soma found in tree 0")
                if node.t == 2: 
                    # this shouldn't happen, but if there's more axon toward
                    #   soma, start counting from there
                    prev_node = node
                    dist = 0
                dist += node.euclidean_distance(prev_node, node)
                prev_node = node
            tree_root = node
            break

    if tree_root is None:
        return float("nan"), float("nan")

    # make point soma-radius north of soma root
    # do acos(dot product) to get angle of tree root from vertical
    # adjust so 0 is theta=pi and 1 is theta=0
    vert = np.zeros(3)
    vert[1] = 1.0
    root = np.zeros(3)
    root[0] = tree_root.x - soma.x
    root[1] = tree_root.y - soma.y
    root[2] = (tree_root.z - soma.z) * 3.0 # multiply in z scale factor
    theta = angle_between(vert, root) / math.pi
    return theta, dist

