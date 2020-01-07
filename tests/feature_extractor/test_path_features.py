import unittest

import neuron_morphology.features.path as path
from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)


class PathTestCase(unittest.TestCase):
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
                    "z": 101,
                    "radius": 1
                },
                {
                    "id": 2,
                    "parent_id": 0,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 102,
                    "radius": 1
                },
                { # bifurcates
                    "id": 3,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 110,
                    "radius": 1
                },                
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 140,
                    "radius": 1 
                },     
                { # this node backtracks, causing the path distance to differ from the euclidean
                    "id": 11,
                    "parent_id": 4,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 130,
                    "radius": 1 
                },       
                { # bifurcates
                    "id": 5,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 130,
                    "radius": 1 
                },                
                {
                    "id": 6,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 135,
                    "radius": 1 
                },       
                {
                    "id": 7,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 30,
                    "y": 0,
                    "z": 103,
                    "radius": 1 
                },     
                { # bifurcates
                    "id": 8,
                    "parent_id": 2,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 125,
                    "radius": 1 
                },
                {
                    "id": 9,
                    "parent_id": 8,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 126,
                    "radius": 1 
                },
                {
                    "id": 10,
                    "parent_id": 8,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 127,
                    "radius": 1 
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )


class TestMeanContraction(PathTestCase):

    def test_generic(self):
        self.assertAlmostEqual(
            path.mean_contraction(self.morphology),
            0.815431533497303
        )

    def test_specific(self):
        self.assertAlmostEqual(
            path.mean_contraction(
                self.morphology, node_types=[APICAL_DENDRITE]),
            1.0 # only axons backtrack
        )


class TestEarlyBranchPath(PathTestCase):

    def test_generic(self):

        self.assertAlmostEqual(
            path.early_branch_path(self.morphology),
            40 / 70.36087214122114 
            # longest short path distance is 40 on the path starting 3 -> 4
            # 70. ...  is the max_path_distance of this tree
        )


class TestMaxPathDistance(PathTestCase):

    def test_generic(self):
        self.assertAlmostEqual(
            path.max_path_distance(self.morphology),
            70.36087214122114
        )