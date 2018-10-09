import functools
from six import iteritems
from allensdk.core.simple_tree import SimpleTree
import allensdk.neuron_morphology.validation as validation
from allensdk.neuron_morphology.validation.result import InvalidMorphology
from allensdk.neuron_morphology.constants import *
import numpy as np
import math
import copy


class Tree(SimpleTree):

    def __init__(self, nodes, node_id_cb, parent_id_cb, strict_validation=False):

        self._nodes = {node_id_cb(n): n for n in nodes}
        self.__parent_id_cb = lambda node: parent_id_cb(node) if parent_id_cb(node) in self._nodes else None
        self._parent_ids = {nid: self.__parent_id_cb(n) for nid, n in iteritems(self._nodes)}
        self._child_ids = {nid: [] for nid in self._nodes}

        for nid in self._parent_ids:
            pid = self._parent_ids[nid]
            if pid is not None:
                self._child_ids[pid].append(nid)

        self.node_id_cb = node_id_cb
        self.parent_id_cb = self.__parent_id_cb

        errors = validation.validate_morphology(self)
        reportable_errors = [e for e in errors if strict_validation or e.level == "Error"]
        if reportable_errors:
            raise InvalidMorphology(reportable_errors)

    def __len__(self):
        return len(self._nodes)

    def children_of(self, node):
        return self.children([node['id']])[0]

    def parent_of(self, node):
        return self.parents([node['id']])[0]

    def get_children_of_node_by_types(self, node, node_types):
        print("node %s" % node)
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

    def get_root(self):
        return self.filter_nodes(lambda node: self.parent_id_cb(node) is None)[0]

    def get_root_id(self):
        return self.node_id_cb(self.get_root())

    def get_independent_axon_nodes(self):
        return self.filter_nodes(lambda node: self.parent_id_cb(node) is None and node['type'] == AXON)

    def get_tree_roots(self):
        axon_roots = self.get_independent_axon_nodes()
        soma_root = self.get_root()
        if axon_roots:
            return axon_roots.append(soma_root)
        return [soma_root]

    def get_number_of_trees(self):
        return len(self.get_tree_list())

    def get_tree_list(self):
        tree_list = []
        tree_roots = self.get_tree_roots()
        for tree_root in tree_roots:
            tree = list(self.children_of(tree_root)).append(tree_root)
            tree_list.append(tree)
        return tree_list

    def get_tree_root(self, tree_number):
        return self.get_tree_list()[tree_number]

    def get_node_by_types(self, node_types):

        if node_types:
            node_by_types = []
            for node_type in node_types:
                node_by_types += self.filter_nodes(lambda node: node['type'] == node_type)
            return node_by_types
        else:
            return self.nodes()

    def get_non_soma_nodes(self):
        return self.filter_nodes(lambda node: node['type'] != SOMA)

    def get_max_id(self):
        return max(self._nodes)

    def get_segment_list(self, node_types=None):

        nodes = self.get_node_by_types(node_types)
        segment_list = []
        for node in nodes:
            if node['type'] is not SOMA:
                if self.is_node_at_end_of_segment(node):
                    segment_list.append(self._build_segment(node))
        return segment_list

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

        branch_order = []
        to_visit = [self.get_root()]

        while to_visit:
            visiting_node = to_visit.pop()
            parent_node_branch_order = [item[1] for item in branch_order if item[0] is self.parent_of(visiting_node)]
            parent_node = self.parent_of(visiting_node)
            nodes_branch_order = None
            if visiting_node['type'] is SOMA:
                nodes_branch_order = 0
            elif parent_node and parent_node['type'] is SOMA:
                nodes_branch_order = 1
            elif parent_node and len(self.children_of(parent_node)) > 1:
                nodes_branch_order = parent_node_branch_order[0] + 1
            elif parent_node and len(self.children_of(parent_node)) <= 1:
                nodes_branch_order = parent_node_branch_order[0]

            if node == visiting_node:
                return nodes_branch_order
            branch_order.append((visiting_node, nodes_branch_order))
            to_visit.extend(self.children_of(visiting_node))

        return None

    def get_branch_order_for_segment(self, segment):
        return self.get_branch_order_for_node(segment[-1])

    def _build_segment(self, end_node):
        segment = [end_node]
        current_node = self.parent_of(end_node)
        if current_node:
            segment.append(current_node)
            while not self.is_node_at_beginning_of_segment(current_node):
                current_node = self.parent_of(current_node)
                if current_node['type'] is SOMA:
                    break
                segment.append(current_node)
        segment.reverse()
        return segment

    def is_node_at_beginning_of_segment(self, node):
        parent = self.parent_of(node)
        children = self.children_of(node)
        is_branching_point = children and len(self.children_of(node)) > 1
        return not parent or is_branching_point

    def is_node_at_end_of_segment(self, node):
        children = self.children_of(node)
        is_branching_point = children and len(children) > 1
        is_leaf_node = not children
        return is_branching_point or is_leaf_node

    def get_compartment_list(self, node_types=None):

        nodes = self.get_node_by_types(node_types)
        compartment_list = []
        for node in nodes:
            for child in self.children_of(node):
                compartment = [node, child]
                compartment_list.append(compartment)
        return compartment_list

    def get_compartment_for_node(self, node):

        compartments = self.get_compartment_list()

        for compartment in compartments:
            if node in compartment:
                return compartment
            else:
                return None

    def get_compartment_length(self, compartment):
        return self.euclidean_distance(compartment[0], compartment[1])

    def get_compartment_midpoint(self, compartment):
        return self.midpoint(compartment[0], compartment[1])

    def clone(self):
        return copy.deepcopy(self)

    def build_intermediate_nodes(self, make_intermediates_cb, set_parent_id_cb):

        visit = functools.partial(self._make_and_insert_intermediate, make_intermediates_cb, set_parent_id_cb)
        self.breadth_first_traversal(visit)

    def _insert_between(self, new_node, parent_id, child_id, set_parent_id_cb):

        node_id = self._node_id_cb(new_node)
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
                must be neighbor_cb(list of node ids) -> list of node_ids. Defaults to self.child_ids.

            start_id : hashable, optional
                Begin the traversal from this node. Defaults to self.get_root_id().

            Notes
            -----
            assumes rooted, acyclic

        """

        if neighbor_cb is None:
            neighbor_cb = self.child_ids

        if start_id is None:
            start_id = self.get_root_id()

        neighbor_ids = [start_id]
        visited_ids = set([])

        while len(neighbor_ids) > 0:
            current_id = neighbor_ids.pop()
            current_node = self.nodes([current_id])[0]

            visit(current_node)
            visited_ids.update([current_id])

            new_neighbor_ids = neighbor_cb([current_id])[0]
            new_neighbor_ids = set(new_neighbor_ids) - visited_ids
            neighbor_ids = list(new_neighbor_ids) + neighbor_ids

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

    def _get_node_attributes(self, attributes, node_types):

        node_attributes = {}
        if node_types is None:
            nodes = self.nodes()
        else:
            nodes = self.get_node_by_types(node_types)
        for node in nodes:
            for attribute in attributes:
                node_attributes.setdefault(attribute, []).append(node[attribute])
        return node_attributes

    def get_dimensions(self, node_types=None):

        node_attributes = self._get_node_attributes(['x', 'y', 'z'], node_types)
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

    def get_scaling_factor_from_affine(self, affine):

        """ Calculates the scaling factor from the affine Matrix. Determinant
            is the change in volume that occurs during transformation. You can get
            the scaling factor by taking the 3rd root of the determinant.

            Format of the affine matrix is:

            [x0 y0 z0 tx]
            [x1 y1 z1 ty]
            [x2 y2 z2 tz]
            [0  0  0  1]

            where the left 3x3 the matrix defines the affine rotation
            and scaling, and the right column is the translation
            vector.

            Parameters
            ----------

            affine: 4x4 numpy matrix

            Returns
            -------

            scaling_factor: double

        """

        determinant = np.linalg.det(affine)
        return math.pow(abs(determinant), 1.0/3.0)

    def apply_affine(self, affine):

        """ Apply an affine transform to all nodes in this
            morphology. Compartment radius is adjusted as well.

            Format of the affine matrix is:

            [x0 y0 z0 tx]
            [x1 y1 z1 ty]
            [x2 y2 z2 tz]
            [0  0  0  1]

            where the left 3x3 the matrix defines the affine rotation
            and scaling, and the right column is the translation
            vector.


            Parameters
            ----------

            affine: 4x4 numpy matrix

        """

        morphology = self.clone()
        scaling_factor = self.get_scaling_factor_from_affine(affine)

        for node in morphology.nodes():
            coordinates = np.array((node['x'], node['y'], node['z'], 1), dtype=float)
            new_coordinates = np.dot(affine, coordinates)
            node['x'] = new_coordinates[0]
            node['y'] = new_coordinates[1]
            node['z'] = new_coordinates[2]
            node['radius'] *= scaling_factor

        return morphology

    def euclidean_distance(self, node1, node2):
        node1_location = np.array((node1['x'], node1['y'], node1['z']))
        node2_location = np.array((node2['x'], node2['y'], node2['z']))
        return np.linalg.norm(node1_location - node2_location)

    def midpoint(self, node1, node2):
        px = (node1['x'] + node2['x']) * 0.5
        py = (node1['y'] + node2['y']) * 0.5
        pz = (node1['z'] + node2['z']) * 0.5
        return [px, py, pz]
