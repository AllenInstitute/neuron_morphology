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

    def test_number_of_branches_by_types(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .basal_dendrite(1, 0, 0)
                        .basal_dendrite(2, 0, 0)
                            .basal_dendrite(2, 1, 0)
                                .basal_dendrite(1, 2, 0).up()
                                .basal_dendrite(3, 2, 0).up(2)
                            .axon(2, -1, 0)
                                .axon(1.5, -2, 0).up()
                                .axon(2.5, -2, 0).up(4)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                            .apical_dendrite(-1, 3, 0).up()
                            .apical_dendrite(1, 3, 0)

                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(ic.num_branches, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.num_branches"], 10)
        self.assertEqual(feature_extraction_run.results["axon.num_branches"], 3)
        self.assertEqual(feature_extraction_run.results["dendrite.num_branches"], 6)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.num_branches"], 3)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.num_branches"], 3)

    def test_max_branch_order_by_types(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .basal_dendrite(1, 0, 0)
                        .basal_dendrite(2, 0, 0)
                            .basal_dendrite(2, 1, 0)
                                .basal_dendrite(1, 2, 0).up()
                                .basal_dendrite(3, 2, 0).up(2)
                            .axon(2, -1, 0)
                                .axon(1.5, -2, 0).up()
                                .axon(2.5, -2, 0).up(4)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                            .apical_dendrite(-1, 3, 0).up()
                            .apical_dendrite(1, 3, 0)

                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(ic.max_branch_order, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["axon.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["dendrite.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.max_branch_order"], 2)

