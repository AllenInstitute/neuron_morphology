import functools
from six import iteritems
from allensdk.core.simple_tree import SimpleTree
import allensdk.neuron_morphology.validation as validation
from allensdk.neuron_morphology.validation.result import InvalidMorphology
from allensdk.neuron_morphology.constants import *
import numpy as np


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

    def node_by_id(self, node_id):
        return self._nodes[node_id]

    def get_root(self):
        return self.filter_nodes(lambda node: self.parent_id_cb(node) is None)[0]

    def get_root_id(self):
        return self.node_id_cb(self.get_root())

    def get_node_by_type(self, node_type):
        return self.filter_nodes(lambda node: node['type'] == node_type)

    def get_max_id(self):
        return max(self._nodes)

    def get_segment_list(self):

        segment_list = []
        for node in self.nodes():
            if node['type'] is not SOMA:
                if self.is_node_at_end_of_segment(node):
                    segment_list.append(self._build_segment(node))
        return segment_list

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
        is_branching_point = children and len(children) > 1
        return not parent or is_branching_point

    def is_node_at_end_of_segment(self, node):
        children = self.children_of(node)
        is_branching_point = children and len(children) > 1
        is_leaf_node = not children
        return is_branching_point or is_leaf_node

    def get_compartment_list(self):

        compartment_list = []
        for node in self.nodes():
            for child in self.children_of(node):
                compartment = [node, child]
                compartment_list.append(compartment)
        return compartment_list

    def get_compartment_length(self, compartment):

        node1_location = np.array((compartment[0]['x'], compartment[0]['y'], compartment[0]['z']))
        node2_location = np.array((compartment[1]['x'], compartment[1]['y'], compartment[1]['z']))
        return np.linalg.norm(node1_location - node2_location)

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
            Will be used during traversal to find the next nodes to be visisted. Signature
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

    def swap_nodes_edges(self, merge_cb=None, node_id_cb=None, parent_id_cb=None, make_root_cb=None, start_id=None):

        """ Build a new tree whose nodes are the edges of this tree and vice-versa

        Parameters
        ----------

        merge_cb : callable, optional

        node_id_cb : callable, optional

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

    def get_dimensions(self):

        min_x = self._nodes[0]["x"]
        max_x = self._nodes[0]["x"]
        min_y = self._nodes[0]["y"]
        max_y = self._nodes[0]["y"]
        min_z = self._nodes[0]["z"]
        max_z = self._nodes[0]["z"]

        for node in self._nodes:

            max_x = max(node.x, max_x)
            max_y = max(node.y, max_y)
            max_z = max(node.z, max_z)

            min_x = min(node.x, min_x)
            min_y = min(node.y, min_y)
            min_z = min(node.z, min_z)

        width = max_x - min_x
        height = max_y - min_y
        depth = max_z - min_z

        return [width, height, depth], [min_x, min_y, min_z], [max_x, max_y, max_z]
