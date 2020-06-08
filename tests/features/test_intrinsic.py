import unittest

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.marked_feature import (
    specialize
)
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS
)
from neuron_morphology.features.intrinsic import (
    num_branches,
    max_branch_order
)


class TestIntrinsic(unittest.TestCase):

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
        fe.register_features([specialize(num_branches, NEURITE_SPECIALIZATIONS)])
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
        fe.register_features([specialize(max_branch_order, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["axon.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["dendrite.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.max_branch_order"], 3)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.max_branch_order"], 2)

