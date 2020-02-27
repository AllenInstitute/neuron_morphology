import unittest

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.morphology_builder import MorphologyBuilder

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS)
from neuron_morphology.feature_extractor.marked_feature import specialize

from neuron_morphology.features import intrinsic as ic


class TestIntrinsic(unittest.TestCase):

    def setUp(self):

        # Create an axon that branches once,
        # and a basal dendrite that has a bifurcation and a trifurcation
        self.morphology = (
            MorphologyBuilder()
                .root()
                    .axon()
                        .axon()
                            .axon()
                                .axon().up()
                                .axon().up(4)
                    .basal_dendrite()
                        .basal_dendrite()
                            .basal_dendrite().up()
                            .basal_dendrite()
                                .basal_dendrite().up()
                                .basal_dendrite().up()
                                .basal_dendrite()
                .build()
        )

        self.data = Data(self.morphology)

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
            extractor.extract(self.data).results
        )

    def test_all_neurites_num_nodes(self):
        self.assertEqual(
            self.extract(self.num_nodes)['all_neurites.num_nodes'],
            13)

    def test_all_neurites_num_tips(self):
        self.assertEqual(
            self.extract(self.num_tips)['all_neurites.num_tips'],
            6)

    def test_all_neurites_num_branches(self):
        self.assertEqual(
            self.extract(self.num_branches)['all_neurites.num_branches'],
            10)

    def test_all_neurites_max_branch_order(self):
        self.assertEqual(
            self.extract(self.max_branch_order)['all_neurites.max_branch_order'],
            3)

    def test_all_neurites_mean_fragmentation(self):
        self.assertAlmostEqual(
            self.extract(self.mean_fragmentation)['all_neurites.mean_fragmentation'],
            13/10)  # 13 compartments in 10 branches
