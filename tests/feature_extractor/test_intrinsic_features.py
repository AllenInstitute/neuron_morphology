import unittest

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    AXON, APICAL_DENDRITE, BASAL_DENDRITE, SOMA
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE_SPECIALIZATIONS
from neuron_morphology.features import intrinsic as ic
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS)
from neuron_morphology.feature_extractor.marked_feature import specialize


class TestOverlap(unittest.TestCase):

    def setUp(self):

        # Create an axon that extends positively and branches once,
        # and a basal dendrite that extends negatively and branches twice
        self.one_dim_neuron = Morphology([
                {
                    "id": 0,
                    "parent_id": -1,
                    "type": SOMA,
                    "x": 0,
                    "y": 100,
                    "z": 0,
                    "radius": 10
                },
                # Axon node [100, 125, 150, 175, 200]
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 100,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 2,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 125,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 3,
                    "parent_id": 2,
                    "type": AXON,
                    "x": 0,
                    "y": 150,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 10,
                    "y": 175,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 5,
                    "parent_id": 3,
                    "type": AXON,
                    "x": -10,
                    "y": 175,
                    "z": 0,
                    "radius": 3
                },
                # Basal node [100, 75, 50]
                {
                    "id": 11,
                    "parent_id": 0,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 100,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 12,
                    "parent_id": 11,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 75,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 13,
                    "parent_id": 12,
                    "type": BASAL_DENDRITE,
                    "x": 10,
                    "y": 50,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 14,
                    "parent_id": 12,
                    "type": BASAL_DENDRITE,
                    "x": -10,
                    "y": 50,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 15,
                    "parent_id": 14,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 25,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 16,
                    "parent_id": 14,
                    "type": BASAL_DENDRITE,
                    "x": -20,
                    "y": 25,
                    "z": 0,
                    "radius": 3
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.one_dim_neuron_data = Data(self.one_dim_neuron)

        self.num_nodes = specialize(
            ic.num_nodes,
            NEURITE_SPECIALIZATIONS)
        self.num_tips = specialize(
            ic.num_tips,
            NEURITE_SPECIALIZATIONS)
        self.num_branches = specialize(
            ic.num_branches,
            NEURITE_SPECIALIZATIONS)
        self.mean_fragmentation = specialize(
            ic.mean_fragmentation,
            NEURITE_SPECIALIZATIONS)
        self.max_branch_order = specialize(
            ic.max_branch_order,
            NEURITE_SPECIALIZATIONS)

    def extract(self, feature):
        extractor = FeatureExtractor([feature])
        return (
            extractor.extract(self.one_dim_neuron_data).results
        )

    def test_all_neurites_num_nodes(self):
        self.assertEqual(
            self.extract(self.num_nodes)['all_neurites.num_nodes'],
            12)

    def test_all_neurites_num_tips(self):
        self.assertEqual(
            self.extract(self.num_tips)['all_neurites.num_tips'],
            5)

    def test_all_neurites_num_branches(self):
        self.assertEqual(
            self.extract(self.num_branches)['all_neurites.num_branches'],
            8)

    def test_all_neurites_max_branch_order(self):
        self.assertEqual(
            self.extract(self.max_branch_order)['all_neurites.max_branch_order'],
            2)

    def test_all_neurites_mean_fragmentation(self):
        self.assertEqual(
            self.extract(self.mean_fragmentation)['all_neurites.mean_fragmentation'],
            1)
