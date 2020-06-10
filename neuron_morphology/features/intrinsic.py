from typing import Optional, List
from functools import partial

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import Intrinsic


@marked(Intrinsic)
def num_tips(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate number of tips

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    # Alternative method:
    num_tips = len(COORD_TYPE.TIP.get_coordinates(data.morphology,
                                                  node_types=node_types))
    return num_tips


@marked(Intrinsic)
def num_nodes(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate number of nodes of a given type

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    num_nodes = len(data.morphology.get_node_by_types(node_types))
    return num_nodes


def child_ids_by_type(node_id, morphology, node_types=None):
    """ Helper function for the traversal functions"""
    node = morphology.node_by_id(node_id)
    children = morphology.get_children(
                    node, node_types=node_types)
    return [child['id'] for child in children]


def calculate_branches_from_root(morphology,
                                 root,
                                 node_types=None):
    """
        Calculate the number of branches of a specific neuron type
        in a morphology. A branch is defined as being between
        two bifurcations or between a bifurcation and a tip
        if a node has three or more children, it is treated as succesive
        bifurcations, e.g a trifurcation: _/_/__ creates 4 branches
        since the branch between the two bifurcations counts

        Parameters
        ----------

        morphology: a morphology object

        root: the root node to traverse from

        node_types: a list of node types (see neuron_morphology constants)
    """
    counter = {'num_branches': 0}

    def branch_visitor(node, counter, node_types):
        num_children = len(morphology.get_children(node,
                                                   node_types=node_types))
        if num_children > 1:
            # branches + (implicit branches from successive bifurcations)
            counter['num_branches'] += num_children + (num_children - 2)
        elif counter['num_branches'] == 0:  # still count root with one child
            counter['num_branches'] += 1

    visitor = partial(branch_visitor,
                      counter=counter,
                      node_types=node_types)
    neighbor_cb = partial(child_ids_by_type,
                          morphology=morphology,
                          node_types=node_types)
    morphology.breadth_first_traversal(visitor,
                                       start_id=morphology.node_id_cb(root),
                                       neighbor_cb=neighbor_cb)
    return counter['num_branches']


@marked(Intrinsic)
def num_branches(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate number of branches

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    morphology = data.morphology
    nodes = morphology.get_node_by_types(node_types)
    roots = morphology.get_roots_for_nodes(nodes)
    num_branches = 0
    for root in roots:
        num_branches += calculate_branches_from_root(
            morphology, root, node_types=node_types)
        if (morphology.parent_of(root) is not None and
            len(morphology.get_children_of_node_by_types(root, node_types)) > 1):
             # if root is a branching node, include the branch that connects root to tree
            num_branches += 1
    return num_branches


def calculate_mean_fragmentation_from_root(morphology,
                                           root,
                                           node_types=None):
    """
        Calculate the mean fragmentation from a root
        in a morphology. Mean fragmentation is the number of compartments
        over the number of branches. A branch is defined as being between
        two bifurcations or between a bifurcation and a tip
        if a node has three or more children, it is treated as succesive
        bifurcations, e.g a trifurcation: _/_/__ creates 4 branches
        since the branch between the two bifurcations counts

        Parameters
        ----------

        morphology: a morphology object

        root: the root node to traverse from

        node_types: a list of node types (see neuron_morphology constants)
    """
    counter = {'num_branches': 0,
               'num_compartments': 0}

    def branch_visitor(node, counter, node_types):
        num_children = len(morphology.get_children(node,
                                                   node_types=node_types))
        if num_children > 1:
            # branches + (implicit branches from successive bifurcations)
            counter['num_branches'] += num_children + (num_children - 2)
            counter['num_compartments'] += num_children + (num_children - 2)
        elif num_children == 1:
            counter['num_compartments'] += 1
            if counter['num_branches'] == 0:  # still count root with one child
                counter['num_branches'] += 1

    visitor = partial(branch_visitor,
                      counter=counter,
                      node_types=node_types)
    neighbor_cb = partial(child_ids_by_type,
                          morphology=morphology,
                          node_types=node_types)
    morphology.breadth_first_traversal(visitor,
                                       start_id=morphology.node_id_cb(root),
                                       neighbor_cb=neighbor_cb)

    mean_fragmentation = counter['num_compartments'] / counter['num_branches']
    return (mean_fragmentation,
            counter['num_branches'],
            counter['num_compartments'])


@marked(Intrinsic)
def mean_fragmentation(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate the mean number of compartments per branch

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    morphology = data.morphology
    roots = morphology.get_roots()
    num_branches = 0
    num_compartments = 0
    for root in roots:
        (_, local_branches, local_compartments) = \
            calculate_mean_fragmentation_from_root(
                morphology, root, node_types=node_types)

        num_branches += local_branches
        num_compartments += local_compartments

    mean_fragmentation = num_compartments / num_branches
    return mean_fragmentation


def calculate_max_branch_order_from_root(morphology,
                                         root,
                                         node_types=None):
    """
        Calculate the greatest number of branches encountered among all 
        directed paths from the morphology's root to its leaves. A branch is 
        defined as a root->leaf ordered path for which:
            1. the first node on the path is either
                a. a bifurcation (has > 1 children)
                b. the root node
            2. the last node on the path is either
                a. a bifurcation
                b. a leaf node (has 0 children)

        Parameters
        ----------
        morphology: the reconstruction whose max branch order will be 
            calculated
        root: treat this node as root
        node_types: If not None, consider only root->leaf paths whose leaf 
            nodes are among these types (see neuron_morphology constants)

        Returns
        -------
        The greatest branch count encountered among all considered root->leaf 
        paths 

    """

    root_id = morphology.node_id_cb(root)
    counter = {'branches_to_node': {root_id: 0},
               'max_branches': 0}

    def branch_visitor(node, counter, node_types):
        cur_branches = counter['branches_to_node'][node['id']]
        children = morphology.get_children(node)
        num_children = len(children)

        if num_children > 1:
            for child in children:
                counter['branches_to_node'][child['id']] = \
                    cur_branches + 1
        elif num_children == 1:
            if cur_branches == 0:
                # create a branch even if its just the root + one node
                counter['branches_to_node'][children[0]['id']] = 1
            else:
                counter['branches_to_node'][children[0]['id']] = cur_branches
        elif num_children == 0 and (node_types is None or node['type'] in node_types):
            if cur_branches > counter['max_branches']:
                counter['max_branches'] = cur_branches

    visitor = partial(branch_visitor,
                      counter=counter,
                      node_types=node_types)
    morphology.depth_first_traversal(visitor,
                                     start_id=root_id)


    return counter['max_branches']


@marked(Intrinsic)
def max_branch_order(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate mean fragmentation

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    morphology = data.morphology
    roots = morphology.get_roots()
    max_branch_order = 0
    for root in roots:
        local_max = calculate_max_branch_order_from_root(
                morphology, root, node_types=node_types)
        if local_max > max_branch_order:
            max_branch_order = local_max

    return max_branch_order
