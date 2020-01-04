import unittest

from neuron_morphology.features import size
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)
from neuron_morphology.morphology import Morphology


class TestTotalLength(unittest.TestCase):

    def setUp(self):

        """
        This morphology looks like:
        S -10-> A -10-> A
        |
        3-> AD -3-> AD
        """
        self.morphology = Morphology([
                {
                    "id": 0,
                    "parent_id": -1,
                    "type": SOMA,
                    "x": 0,
                    "y": 0,
                    "z": 100,
                    "radius": 1
                },
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 110,
                    "radius": 1
                },
                {
                    "id": 2,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 120,
                    "radius": 1
                },
                {
                    "id": 3,
                    "parent_id": 0,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 3,
                    "z": 100,
                    "radius": 1
                },
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 6,
                    "z": 100,
                    "radius": 1
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

    def test_generic(self):
        obtained = size.total_length(self.morphology)
        self.assertEqual(obtained, 13)

    def test_restricted(self):
        obtained = size.total_length(self.morphology, [AXON])
        self.assertEqual(obtained, 10)