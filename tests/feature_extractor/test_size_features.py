import unittest
import math
import copy as cp

import numpy as np

from neuron_morphology.features import size
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)
from neuron_morphology.morphology import Morphology


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
    ]


class MorphoSizeTest(unittest.TestCase):
    def setUp(self):
        self.morphology = Morphology(
            basic_nodes(),
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

class TestTotalLength(MorphoSizeTest):

    def test_generic(self):
        obtained = size.total_length(self.morphology)
        self.assertEqual(obtained, 13)

    def test_restricted(self):
        obtained = size.total_length(self.morphology, [AXON])
        self.assertEqual(obtained, 10)


class TestTotalSurfaceArea(MorphoSizeTest):
    # see morphology tests for tests that vary radii

    def test_generic(self):
        self.assertAlmostEqual(
            size.total_surface_area(self.morphology),
            math.pi * 4 * 13 # all radii == 1, 4 compartments, 13 total length
        )

    def test_restricted(self):
        self.assertAlmostEqual(
            size.total_surface_area(self.morphology, [AXON]),
            math.pi * 2 * 10
        )


class TestMeanDiameter(unittest.TestCase):

    def setUp(self):
        nodes = basic_nodes()
        self.sizes = np.random.rand(len(nodes))
        
        for sz, node in zip(self.sizes, nodes):
            node["radius"] = sz

        self.morphology = Morphology(
            nodes,
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.mean_diameter = np.mean(self.sizes) * 2

    def test_generic(self):
        self.assertAlmostEqual(
            size.mean_diameter(self.morphology),
            self.mean_diameter
        )


class TestMeanParentDaughterRatio(unittest.TestCase):

    def setUp(self):
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
                    "radius": 20
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
                    "radius": 10
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
        self.assertAlmostEqual(
            size.mean_parent_daughter_ratio(self.morphology),
            (1/20 + 1/10 + 20 + 10) / 4
        )

    def test_restricted(self):
        self.assertAlmostEqual(
            size.mean_parent_daughter_ratio(self.morphology, [SOMA, AXON]),
            (1/20 + 20) / 2
        )


class TestMaxEuclideanDistance(MorphoSizeTest):

    def test_generic(self):
        self.assertAlmostEqual(
            size.max_euclidean_distance(self.morphology),
            20
        )

    def test_restricted(self):
        self.assertAlmostEqual(
            size.max_euclidean_distance(self.morphology, [APICAL_DENDRITE]),
            6
        )