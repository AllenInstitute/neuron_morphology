from typing import Sequence, Dict
from statistics import mean
import functools
from collections import deque
from six import iteritems
from allensdk.core.simple_tree import SimpleTree
import neuron_morphology.validation as validation
from neuron_morphology.validation.result import InvalidMorphology
from neuron_morphology.constants import *
from scipy.spatial.distance import euclidean
import numpy as np
import copy
import queue
import math


class Morphology(SimpleTree):

    def __init__(self, nodes, node_id_cb, parent_id_cb):

        self._nodes = {node_id_cb(n): n for n in nodes}
        self._parent_id_cb = lambda node: parent_id_cb(node) if parent_id_cb(node) in self._nodes else None
        self._parent_ids = {nid: self._parent_id_cb(n) for nid, n in iteritems(self._nodes)}
        self._child_ids = {nid: [] for nid in self._nodes}
        self.compartments_for_nodes = {}

        for nid in self._parent_ids:
            pid = self._parent_ids[nid]
            if pid is not None:
                self._child_ids[pid].append(nid)

        self.node_id_cb = node_id_cb
        self.parent_id_cb = self._parent_id_cb
        self.nodes_by_types = {}
        self._create_compartment_dictionary()
        self.compartments = self.get_compartments()

    def __len__(self):
        return len(self._nodes)

    def validate(self, strict=False):
        """ 
        Validate the neuron morphology in 
            [bits, radius, resample, type, structure]
        """

        errors = validation.validate_morphology(self)
        reportable_errors = [e for e in errors if strict or e.level == "Error"]
        if reportable_errors:
            raise InvalidMorphology(reportable_errors)
        return None

    def children_of(self, node):
        if node:
            children = self.children([node['id']])
            if children:
                return children[0]
        return None

    def parent_of(self, node):
        if node:
            parent = self.parents([node['id']])
            if parent:
                return parent[0]
        return None

    def get_children_of_node_by_types(self, node, node_types):
        children = self.children_of(node)
        children_by_types = []
        for child in children:
            if child['type'] in node_types:
                children_by_types.append(child)
        return children_by_types

    def get_children(self, node, node_types=None):
        if node_types:
            return self.get_children_of_node_by_types(node, node_types)
        else:
            return self.children_of(node)

    def node_by_id(self, node_id):
        return self._nodes[node_id]

    def get_soma(self):
        """
        Return one soma node labeled with SOMA
        If the input SWC file does not have any node labeled with SOMA,
        it will return None

        Parameters
        ----------
        morphology: Morphology object

        Returns
        -------

        Soma node object

        """
        soma = None
        somaList = self.get_node_by_types([SOMA])
        if somaList:
            soma = somaList[0]
        return soma

    def get_root(self):
        """
        Return the first found root node
        If the input SWC file does not have any root node,
        it will return None

        Parameters
        ----------
        morphology: Morphology object

        Returns
        -------

        Root node object

        """
        root_node = None
        root_nodes = self.filter_nodes(lambda node: self.parent_id_cb(node) is None)
        if root_nodes:
            root_node = root_nodes[0]
        return root_node

    def get_roots(self):
        return self.filter_nodes(lambda node: self.parent_id_cb(node) is None)

    def get_root_id(self):
        return self.node_id_cb(self.get_root())

    def get_roots_for_nodes(self, nodes):
        tree_roots = []
        for node in nodes:
            if self.parent_of(node) not in nodes:
                tree_roots.append(node)
        return tree_roots

    def get_roots_for_analysis(self, root=None, node_types=None):
        """
        Returns a list of all trees to be analyzed, based on the supplied root.
        These trees are the list of all children of the root, if root is
        not None, and the root node of all trees in the morphology if root
        is None.

        Parameters
        ----------
        morphology: Morphology object

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
            nodes = self.get_node_by_types(node_types)

            roots = self.get_roots_for_nodes(nodes)
        else:
            roots = self.get_children(root, node_types)
        return roots

    def get_number_of_trees(self, nodes=None):
        if nodes:
            roots = self.get_roots_for_nodes(nodes)
        else:
            roots = self.get_roots()
        return len(roots)

    def get_tree_list(self):
        tree_list = []
        tree_roots = self.get_roots()
        for tree_root in tree_roots:
            tree = []
            tree_queue = queue.Queue()
            tree_queue.put(tree_root)
            while not tree_queue.empty():
                root = tree_queue.get()
                tree.append(root)
                children = self.children_of(root)
                if children:
                    for child in children:
                        tree_queue.put(child)
            tree_list.append(tree)
        return tree_list

    def get_root_for_tree(self, tree_number):
        tree = self.get_tree_list()[tree_number]
        for node in tree:
            parent = self.parent_of(node)
            if not parent:
                return node

    def get_node_by_types(self, node_types=None):
        if node_types:
            node_by_types = []
            for node_type in node_types:
                if node_type not in self.nodes_by_types:
                    self.nodes_by_types[node_type] = self.filter_nodes(lambda node: node['type'] == node_type)
                node_by_types += self.nodes_by_types[node_type]
            return node_by_types
        else:
            return self.nodes()

    def has_type(self, node_type):
        if node_type not in self.nodes_by_types:
            self.nodes_by_types[node_type] = self.filter_nodes(lambda node: node['type'] == node_type)
        if self.nodes_by_types[node_type]:
            return True
        else:
            return False

    def get_non_soma_nodes(self):
        return self.filter_nodes(lambda node: node['type'] != SOMA)

    def get_max_id(self):
        return max(self._nodes)

    def is_soma_child(self, node):
        if self.parent_of(node):
            return self.parent_of(node) and self.parent_of(node)['type'] == SOMA
        return None

    def get_segment_list(self, node_types=None):

        if node_types:
            nodes = self.get_node_by_types(node_types)
        else:
            nodes = self.nodes()
        segment_list = []
        for node in nodes:
            if node['type'] != SOMA:
                if self.is_node_at_end_of_segment(node):
                    segment_list.append(self._build_segment(node))
        return segment_list

    def _build_segment(self, end_node):
        segment = [end_node]
        current_node = self.parent_of(end_node)
        if current_node and current_node['type'] != SOMA:
            segment.append(current_node)
            while current_node and not self.is_node_at_beginning_of_segment(current_node):
                current_node = self.parent_of(current_node)
                if current_node and current_node['type'] == SOMA:
                    break
                elif not current_node:
                    break
                segment.append(current_node)
        segment.reverse()
        return segment

    def is_node_at_beginning_of_segment(self, node):
        is_soma_child = self.is_soma_child(node)
        children = self.children_of(node)
        parent_node = self.parent_of(node)
        if node['type'] != SOMA:
            is_branching_point = children and parent_node and len(self.children_of(parent_node)) > 1
            return is_soma_child or is_branching_point
        return None

    def is_node_at_end_of_segment(self, node):
        children = self.children_of(node)
        is_branching_point = children and len(children) > 1
        is_leaf_node = not children
        return is_branching_point or is_leaf_node

    def get_segment_length(self, segment):
        path_length = 0.0
        if len(segment) < 2:
            return
        parent = segment[0]
        for i in range(1, len(segment)):
            child = segment[i]
            path_length += self.euclidean_distance(parent, child)
            parent = child
        return path_length

    def get_branch_order_for_node(self, node):

        order = 0
        parent = self.parent_of(node)
        while parent:
            if len(self.children_of(parent)) > 1 or parent['type'] == SOMA:
                order += 1
            parent = self.parent_of(parent)
        return order

    def get_branch_order_for_segment(self, segment):
        return self.get_branch_order_for_node(segment[-1])

    def _create_compartment_dictionary(self):

        nodes = self.nodes()
        for node in nodes:
            parent = self.parent_of(node)
            if not parent:
                continue
            compartment = [parent, node]
            self.compartments_for_nodes[node['id']] = compartment

    def get_compartments(self, nodes=None, node_types=None):

        if not nodes:
            nodes = self.nodes()
        compartments = []
        for node in nodes:
            node_id = node['id']
            if node_id in self.compartments_for_nodes:
                compartment = self.compartments_for_nodes[node_id]
                if node_types:
                    if compartment[0]['type'] in node_types:
                        compartments.append(compartment)
                else:
                    compartments.append(compartment)
        return compartments

    def get_compartment_for_node(self, node, node_types=None):

        for node_id, compartment in self.compartments_for_nodes.items():
            if compartment[1] == node:
                if node_types:
                    if compartment[0]['type'] in node_types and compartment[1]['type'] in node_types:
                        return compartment
                    return None
                return compartment
        return None

    def get_compartment_length(self, compartment):
        return self.euclidean_distance(compartment[0], compartment[1])

    def get_compartment_surface_area(self, compartment: Sequence[Dict]) -> float:
        """ Calculate the surface area of a single compartment. Treats the 
        compartment as a circular conic frustum and calculates its lateral 
        surface area. This is:
            pi * (r_1 + r_2) * sqrt( (r_2 - r_1) ** 2 + L ** 2 )

        Parameters
        ----------
        compartment : two-long sequence. Each element is a node and must have 
            3d position data ("x", "y", "z") and a "radius"

        Returns
        -------
        The surface area of the sides of the compartment

        """

        length = self.get_compartment_length(compartment)
        radius_diff = compartment[1]["radius"] - compartment[0]["radius"]
        radius_sum = compartment[1]["radius"] + compartment[0]["radius"]

        slant_height = math.sqrt((radius_diff) ** 2 + length ** 2)
        return math.pi * radius_sum * slant_height

    def get_compartment_volume(self, compartment: Sequence[Dict]) -> float:
        """ Calculate the volume of a single compartment. Treats the 
        compartment as a circular conic frustum and calculates its volume as:
            pi * L * (r_1 ** 2 + r_1 * r_2 + r_2 ** 2) / 3

        Parameters
        ----------
        compartment : two-long sequence. Each element is a node and must have 
            3d position data ("x", "y", "z") and a "radius"
        
        Returns
        -------
        The volume of the compartment

        """

        length = self.get_compartment_length(compartment)
        
        first_rad = compartment[0]["radius"]
        second_rad = compartment[1]["radius"]

        return ( math.pi * length / 3 ) * \
            ( first_rad ** 2 + first_rad * second_rad + second_rad ** 2 )
        

    def get_compartment_midpoint(self, compartment):
        return self.midpoint(compartment[0], compartment[1])

    def get_leaf_nodes(self, node_types=None):
        if not node_types:
            nodes = self.get_non_soma_nodes()
        else:
            nodes = self.get_node_by_types(node_types)

        leaf_nodes = []
        for node in nodes:
            if not self.get_children(node):
                leaf_nodes.append(node)

        return leaf_nodes

    def get_branching_nodes(self, node_types=None):
        if not node_types:
            nodes = self.get_non_soma_nodes()
        else:
            nodes = self.get_node_by_types(node_types)

        branching_nodes = []
        for node in nodes:
            if len(self.get_children(node)) > 1:
                branching_nodes.append(node)

        return branching_nodes

    def clone(self):
        return copy.deepcopy(self)

    def build_intermediate_nodes(self, make_intermediates_cb, set_parent_id_cb):

        visit = functools.partial(self._make_and_insert_intermediate, make_intermediates_cb, set_parent_id_cb)
        self.breadth_first_traversal(visit)

    def _insert_between(self, new_node, parent_id, child_id, set_parent_id_cb):

        node_id = self.node_id_cb(new_node)
        self._nodes[node_id] = new_node

        self._parent_ids[node_id] = parent_id
        self._parent_ids[child_id] = node_id

        if parent_id not in self._child_ids:
            self._child_ids[parent_id] = []

        self._child_ids[parent_id] = list(set(self._child_ids[parent_id]) - {child_id})
        self._child_ids[parent_id].append(node_id)

        if node_id not in self._child_ids:
            self._child_ids[node_id] = []
        self._child_ids[node_id] = [child_id]

        set_parent_id_cb(self._nodes[child_id], node_id)

    def _make_and_insert_intermediate(self, make_intermediates_cb, set_parent_id_cb, child):

        parent_id = self._parent_id_cb(child)
        if parent_id is not None:

            parent = self.nodes([parent_id])[0]
            intermediates = make_intermediates_cb(child, parent, self.get_max_id())

            for ii, new_node in enumerate(intermediates):
                parent_id = self.parent_id_cb(new_node)

                if ii <= len(intermediates) - 1:
                    child_id = self.node_id_cb(child)
                else:
                    child_id = self.node_id_cb(intermediates[ii + 1])

                self._insert_between(new_node, parent_id, child_id, set_parent_id_cb)

    def breadth_first_traversal(self, visit, neighbor_cb=None, start_id=None):

        """ Apply a function to each node of a connected graph in breadth-first order

            Parameters
            ----------

            visit : callable
                Will be applied to each node. Signature must be visit(node). Return is
                ignored.

            neighbor_cb : callable, optional
                Will be used during traversal to find the next nodes to be visited. Signature
                must be neighbor_cb(node id) -> list of node_ids. Defaults to self.child_ids.

            start_id : hashable, optional
                Begin the traversal from this node. Defaults to self.get_root_id().

            Notes
            -----
            assumes rooted, acyclic

        """

        if neighbor_cb is None:
            def child_ids_cb(node_id):
                nested_ids = self.child_ids([node_id])
                return [nid for nids in nested_ids for nid in nids]
            neighbor_cb = child_ids_cb

        if start_id is None:
            start_id = self.get_root_id()

        neighbor_ids = deque([start_id])
        visited_ids = set([])

        while neighbor_ids:
            current_id = neighbor_ids.popleft()
            current_node = self.nodes([current_id])[0]

            visit(current_node)
            visited_ids.update([current_id])

            new_neighbor_ids = neighbor_cb(current_id)
            new_neighbor_ids = set(new_neighbor_ids) - visited_ids
            neighbor_ids.extend(new_neighbor_ids)

    def depth_first_traversal(self, visit, neighbor_cb=None, start_id=None):

        """ Apply a function to each node of a connected graph in depth-first order

            Parameters
            ----------

            visit : callable
                Will be applied to each node. Signature must be visit(node). Return is
                ignored.

            neighbor_cb : callable, optional
                Will be used during traversal to find the next nodes to be visited. Signature
                must be neighbor_cb(node_id) -> list of node_ids. Defaults to self.child_ids.

            start_id : hashable, optional
                Begin the traversal from this node. Defaults to self.get_root_id().

            Notes
            -----
            assumes rooted, acyclic

        """

        if neighbor_cb is None:
            def child_ids_cb(node_id):
                nested_ids = self.child_ids([node_id])
                return [nid for nids in nested_ids for nid in nids]
            neighbor_cb = child_ids_cb

        if start_id is None:
            start_id = self.get_root_id()

        neighbor_ids = deque([start_id])
        visited_ids = set([])

        while neighbor_ids:
            current_id = neighbor_ids.pop()
            current_node = self.nodes([current_id])[0]

            visit(current_node)
            visited_ids.update([current_id])

            new_neighbor_ids = neighbor_cb(current_id)
            new_neighbor_ids = set(new_neighbor_ids) - visited_ids
            neighbor_ids.extend(new_neighbor_ids)

    def swap_nodes_edges(self, merge_cb=None, parent_id_cb=None, make_root_cb=None, start_id=None):

        """ Build a new tree whose nodes are the edges of this tree and vice-versa

            Parameters
            ----------

            merge_cb : callable, optional

            parent_id_cb : callable, optional

            make_root_cb : callable, optional

            start_id : hashable, optional

            Notes
            -----
            assumes rooted, acyclic

        """

        def default_merge_ch(child, parent):
            return {
                'id': self.node_id_cb(child),
                'parent_id': self.node_id_cb(parent),
                'child': child,
                'parent': parent
            }

        if merge_cb is None:
            merge_cb = default_merge_ch

        def default_make_root_cb(tree):
            return {
                'id': tree.get_root_id(),
                'parent_id': None,
                'child': None,
                'parent': None
            }

        if make_root_cb is None:
            make_root_cb= default_make_root_cb

        def node_id_cb(node):
            return node['id']

        if node_id_cb is None:
            node_id_cb = node_id_cb

        new_nodes = [make_root_cb(self)]
        visit = functools.partial(self._get_edge_and_merge, merge_cb, new_nodes)

        self.breadth_first_traversal(visit, start_id=start_id)

        new_node_ids = set([node['id'] for node in new_nodes])
        if parent_id_cb is None:
            parent_id_cb = lambda node: node['parent_id'] if node['parent_id'] in new_node_ids else None

        return self.__class__(new_nodes, node_id_cb=node_id_cb, parent_id_cb=parent_id_cb)

    def _get_edge_and_merge(self, merge_cb, new_nodes, node):

        """Used by swap_nodes_edges
        """

        parent_id = self.parent_id_cb(node)
        if parent_id is not None:
            parent = self.nodes([parent_id])[0]
            new_node = merge_cb(node, parent)
            new_nodes.append(new_node)

    @staticmethod
    def _get_node_attributes(attributes, nodes):

        node_attributes = {}
        for node in nodes:
            for attribute in attributes:
                node_attributes.setdefault(attribute, []).append(node[attribute])
        return node_attributes

    def get_dimensions(self, node_types=None):

        if node_types:
            nodes = self.get_node_by_types(node_types)
            if not nodes:
                return None
        else:
            nodes = self.nodes()

        node_attributes = self._get_node_attributes(['x', 'y', 'z'], nodes)
        node_x = node_attributes['x']
        node_y = node_attributes['y']
        node_z = node_attributes['z']

        min_x = min(node_x)
        max_x = max(node_x)
        min_y = min(node_y)
        max_y = max(node_y)
        min_z = min(node_z)
        max_z = max(node_z)
        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z

        return [width, height, depth], [min_x, min_y, min_z], [max_x, max_y, max_z]

    @staticmethod
    def euclidean_distance(node1, node2):
        node1_location = np.array((node1['x'], node1['y'], node1['z']))
        node2_location = np.array((node2['x'], node2['y'], node2['z']))
        return euclidean(node1_location, node2_location)

    @staticmethod
    def midpoint(node1, node2):
        px = (node1['x'] + node2['x']) * 0.5
        py = (node1['y'] + node2['y']) * 0.5
        pz = (node1['z'] + node2['z']) * 0.5
        return [px, py, pz]
