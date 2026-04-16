# Vendored from allensdk.core.simple_tree (AllenInstitute/AllenSDK).
# Original: Allen Institute Software License (2-clause BSD + non-commercial clause).
# Copyright 2017. Allen Institute. All rights reserved.
#
# Modifications: removed allensdk dependency; replaced allensdk.deprecated
# decorator with an equivalent stdlib implementation.

import functools
import operator as op
import warnings


def _deprecated(message=""):
    """Minimal drop-in for allensdk.deprecated.deprecated."""
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            warnings.warn(
                "Function {0} is deprecated. {1}".format(fn.__name__, message),
                category=DeprecationWarning,
                stacklevel=2,
            )
            return fn(*args, **kwargs)
        return wrapper
    return decorator


class SimpleTree(object):
    def __init__(self, nodes, node_id_cb, parent_id_cb):
        """A tree structure.

        Parameters
        ----------
        nodes : list of dict
            Each dict is a node in the tree.
        node_id_cb : callable
            Given a node dict, returns a unique hashable id for that node.
        parent_id_cb : callable
            Given a node dict, returns the id of that node's parent (or None
            for the root).
        """
        self._nodes = {node_id_cb(n): n for n in nodes}
        self._parent_ids = {
            nid: parent_id_cb(n) for nid, n in self._nodes.items()
        }
        self._child_ids = {nid: [] for nid in self._nodes}

        for nid in self._parent_ids:
            pid = self._parent_ids[nid]
            if pid is not None:
                self._child_ids[pid].append(nid)

        self.node_id_cb = node_id_cb
        self.parent_id_cb = parent_id_cb

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------

    def filter_nodes(self, criterion):
        """Return nodes for which *criterion* is True."""
        return list(filter(criterion, self._nodes.values()))

    def value_map(self, from_fn, to_fn):
        """Return a dict mapping ``from_fn(node)`` → ``to_fn(node)``."""
        vm = {}
        for node in self._nodes.values():
            key = from_fn(node)
            value = to_fn(node)
            if key in vm:
                raise RuntimeError(
                    "from_fn is not unique across nodes. "
                    "Collision between {0} and {1}.".format(value, vm[key])
                )
            vm[key] = value
        return vm

    def nodes_by_property(self, key, values, to_fn=None):
        """Get nodes by a specified property."""
        if to_fn is None:
            def to_fn(x):
                return x

        if not callable(key):
            def from_fn(x):
                return x[key]
        else:
            from_fn = key

        value_map = self.value_map(from_fn, to_fn)
        return [value_map[vv] for vv in values]

    def node_ids(self):
        """Return all node ids."""
        return list(self._nodes)

    # ------------------------------------------------------------------
    # Parent / child / ancestor / descendant ids
    # ------------------------------------------------------------------

    @_deprecated("Use SimpleTree.parent_ids instead.")
    def parent_id(self, node_ids):
        return self.parent_ids(node_ids)

    def parent_ids(self, node_ids):
        """Return the parent id for each id in *node_ids*."""
        return [self._parent_ids[nid] for nid in node_ids]

    def child_ids(self, node_ids):
        """Return a list of children-id-lists for each id in *node_ids*."""
        return [self._child_ids[nid] for nid in node_ids]

    def ancestor_ids(self, node_ids):
        """Return a list of ancestor-id-lists for each id in *node_ids*.

        The ancestor list for node C in A→B→C is [C, B, A].
        """
        out = []
        for nid in node_ids:
            current = [nid]
            while current[-1] is not None:
                current.extend(self.parent_ids([current[-1]]))
            out.append(current[:-1])
        return out

    def descendant_ids(self, node_ids):
        """Return a list of descendant-id-lists for each id in *node_ids*.

        The descendant list for A in A→B→C, A→D is [B, C, D].
        """
        out = []
        for nid in node_ids:
            current = [nid]
            children = self.child_ids([nid])[0]
            if children:
                current.extend(
                    functools.reduce(
                        op.add, map(list, self.descendant_ids(children))
                    )
                )
            out.append(current)
        return out

    # ------------------------------------------------------------------
    # Parent / child / ancestor / descendant nodes
    # ------------------------------------------------------------------

    @_deprecated("Use SimpleTree.nodes instead")
    def node(self, node_ids=None):
        return self.nodes(node_ids)

    def nodes(self, node_ids=None):
        """Return node dicts for the given ids (all nodes if None)."""
        if node_ids is None:
            node_ids = self.node_ids()
        return [
            self._nodes[nid] if nid in self._nodes else None
            for nid in node_ids
        ]

    @_deprecated("Use SimpleTree.parents instead")
    def parent(self, node_ids):
        return self.parents(node_ids)

    def parents(self, node_ids):
        """Return the parent node dict for each id in *node_ids*."""
        return self.nodes([self._parent_ids[nid] for nid in node_ids])

    def children(self, node_ids):
        """Return a list of children-node-lists for each id in *node_ids*."""
        return list(map(self.nodes, self.child_ids(node_ids)))

    def descendants(self, node_ids):
        """Return a list of descendant-node-lists for each id in *node_ids*."""
        return list(map(self.nodes, self.descendant_ids(node_ids)))

    def ancestors(self, node_ids):
        """Return a list of ancestor-node-lists for each id in *node_ids*."""
        return list(map(self.nodes, self.ancestor_ids(node_ids)))
