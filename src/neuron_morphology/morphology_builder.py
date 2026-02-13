import warnings
import random

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)

class MorphologyBuilder:
    
    @property
    def next_id(self):
        result = self._id
        self._id += 1
        return result
        
    @property
    def parent_id(self):
        return self._parent_queue[-1] if self._parent_queue else -1

    @property
    def active_node_id(self):
        if self._parent_queue:
            return self._parent_queue[-1]
    
    def __init__(self):
        """ A utility for putting together a morphology object using succinct,
        declarative code. See tests/test_morphology_builder.py for example 
        usage.
        """

        self._id = 0
        self._parent_queue = []
        self.nodes = []
        self.rng = random.Random()
        
    def up(self, by=1):
        """ Terminate a branch. Set the active node to the previous active 
        node's ancestor.

        Parameters
        ----------
        by : how far (up the tree) to set the new active node. Default is the 
            parent of the current node (1). 2 would correspond to the 

        """

        for _ in range(by):
            if self._parent_queue:
                self._parent_queue.pop()
            else:
                warnings.warn(
                    f"this {self.__class__.__name__}'s active node has been "
                    "unset. If you wish to add more nodes from this point "
                    "you must use .root() to create a new root"
                )
        return self
        
    def root(self, x=0, y=0, z=0, node_type=SOMA, radius=1):
        """ Add a new root node (parent -1) to this reconstruction. This will 
        be the new active node.
        """

        self._parent_queue = []
        return self._add_node(x, y, z, node_type, radius)
    
    def child(self, x, y, z, node_type, radius=1):
        """ Add a child node to the current active node. This will become the 
        new active node.
        """

        if not self._parent_queue:
            raise ValueError(
                "attempted to create a child node, but the active node is "
                "unset. If you wish to add more nodes from this point "
                "you must use .root() to create a new root"
            )
        return self._add_node(x, y, z, node_type, radius)
        
    def _add_node(self, x, y, z, node_type, radius):
        """ Add a new node to this morphology.

        Parameters
        ----------
        x : x coordinate of this node's position
        y : y coordinate of this node's position
        z : z coordinate of this node's position
        node_type : one of AXON, SOMA, APICAL_DENDRITE, BASAL_DENDRITE
        radius : describe the size of this node

        """

        node_id = self.next_id

        self.nodes.append({
            "x": x if x is not None else self.rng.uniform(-1, 1),
            "y": y if y is not None else self.rng.uniform(-1, 1),
            "z": z if z is not None else self.rng.uniform(-1, 1),
            "radius": radius,
            "type": node_type,
            "id": node_id,
            "parent": self.parent_id
        })
        self._parent_queue.append(node_id)
        return self

    def axon(self, x=None, y=None, z=None, radius=1):
        """ Convenvience for creating an axon node. Will not create a root.
        """
        return self.child(x, y, z, AXON, radius)

    def apical_dendrite(self, x=None, y=None, z=None, radius=1):
        """ Convenvience for creating an apical dendrite node. Will not create 
        a root.
        """
        return self.child(x, y, z, APICAL_DENDRITE, radius)

    def basal_dendrite(self, x=None, y=None, z=None, radius=1):
        """ Convenvience for creating a basal dendrite node. Will not create a 
        root.
        """
        return self.child(x, y, z, BASAL_DENDRITE, radius)
        
    def build(self):
        """ Construct a Morphology object using this builder. This is a non-
        destructive operation. The Morphology will be validated at this stage.
        """

        return Morphology(
            self.nodes, 
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent"]
        )
