
from neuron_morphology.morphology import Morphology
from neuron_morphology.node import Node


def test_node(id=1, type=Morphology.SOMA, x=0, y=0, z=0, radius=1, parent_node_id=-1):
    return Node(id, type, x, y, z, radius, parent_node_id)