from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import SOMA

class MorphologyBuilder:
    
    @property
    def next_id(self):
        result = self._id
        self._id += 1
        return result
        
    @property
    def parent_id(self):
        return self._parent_queue[-1] if self._parent_queue else -1
    
    def __init__(self):
        """ A utility for putting together a morphology object using succinct,
        declarative code.
        """

        self._id = 0
        self._parent_queue = []
        self.nodes = []
        
    def up(self, by=1):
        for _ in range(by):
            self._parent_queue.pop()
        return self
        
    def root(self, x, y, z, node_type=SOMA, radius=1):
        return self._add_node(x, y, z, node_type, radius, -1)
    
    def child(self, x, y, z, node_type, radius=1):
        return self._add_node(x, y, z, node_type, radius)
        
    def _add_node(self, x, y, z, node_type, radius, parent_id=None):
        node_id = self.next_id
        parent_id = self.parent_id if parent_id is None else parent_id

        self.nodes.append({
            "x": x,
            "y": y,
            "z": z,
            "radius": radius,
            "type": node_type,
            "id": node_id,
            "parent_id": parent_id
        })
        self._parent_queue.append(node_id)
        return self
        
    def build(self):
        return Morphology(
            self.nodes, 
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"]
        )
