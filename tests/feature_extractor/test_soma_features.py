import unittest

import numpy as np
import math
from neuron_morphology.features import soma
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)
from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.data import Data

def basic_nodes():
    """
    This morphology looks like:
    S -10-> A -10-> A
    |
    3-> AD -3-> AD
    """
    return [
        {
            "id": 0,
            "parent_id": -1,
            "type": SOMA,
            "x": 0,
            "y": 0,
            "z": 100,
            "radius": 5
        },
        {
            "id": 1,
            "parent_id": -1,
            "type": AXON,
            "x": 1,
            "y": 5,
            "z": 110,
            "radius": 1
        },
        {
            "id": 2,
            "parent_id": 1,
            "type": AXON,
            "x": 3,
            "y": 10,
            "z": 120,
            "radius": 1
        },
        {
            "id": 3,
            "parent_id": 0,
            "type": APICAL_DENDRITE,
            "x": 5,
            "y": 15,
            "z": 100,
            "radius": 1
        },
        {
            "id": 4,
            "parent_id": 3,
            "type": APICAL_DENDRITE,
            "x": 7,
            "y": 20,
            "z": 100,
            "radius": 1
        },
    ]


class MorphSomaTest(unittest.TestCase):
    def setUp(self):
        self.morphology = Morphology(
            basic_nodes(),
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )
        self.data = Data(self.morphology, relative_soma_depth= 0.25)

class TestSomaFeatures(MorphSomaTest):
    
    def test_soma_surface(self):
        obtained = soma.calculate_soma_surface(self.data)
        self.assertAlmostEqual(obtained, 4.0 * math.pi * 5 * 5)

    def test_relative_soma_depth(self):
        obtained = soma.calculate_relative_soma_depth(self.data)
        self.assertAlmostEqual(obtained, 0.25)

    def test_stem_exit_and_distance(self):
        first, second = soma.calculate_stem_exit_and_distance(self.data, [AXON])
        self.assertAlmostEqual(first, 0.447, 3)
        self.assertAlmostEqual(second, 11.22, 2)


class TestSomaPercentile(unittest.TestCase):
    def setUp(self):
        # morphology with 3/4 axons below soma in z
        self.morphology = Morphology([
            {
                "id": 0,
                "parent_id": -1,
                "type": SOMA,
                "x": 0,
                "y": 0,
                "z": 100,
                "radius": 5
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
                "z": 90,
                "radius": 1
            },
            {
                "id": 3,
                "parent_id": 2,
                "type": AXON,
                "x": 0,
                "y": 0,
                "z": 80,
                "radius": 1
            },
            {
                "id": 4,
                "parent_id": 3,
                "type": AXON,
                "x": 0,
                "y": 0,
                "z": 70,
                "radius": 1
            },
        ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.data = Data(self.morphology)

    def test_soma_percentile(self):
        obtained = soma.soma_percentile(self.data, [AXON])
        self.assertEqual(obtained[2], 0.25)

    def test_soma_percentile_no_sym(self):
        obtained = soma.soma_percentile(self.data, [AXON], symmetrize_xz=False)
        self.assertEqual(obtained[2], 0.75)
