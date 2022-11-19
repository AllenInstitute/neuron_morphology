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
from neuron_morphology.features.path import (
    max_path_distance, mean_contraction
)


class TestPath(unittest.TestCase):

    def test_contraction(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .basal_dendrite(1, 0, 0)
                        .basal_dendrite(2, 0, 0)
                            .basal_dendrite(2, 1, 0)
                                .basal_dendrite(1, 1, 0).up()
                                .basal_dendrite(3, 1, 0).up(2)
                            .axon(2, -1, 0)
                                .axon(2, -2, 0)
                                    .axon(1, -2, 0).up()
                                    .axon(3, -2, 0).up(5)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                            .apical_dendrite(-1, 2, 0).up()
                            .apical_dendrite(1, 2, 0)
                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(mean_contraction, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["axon.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["dendrite.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.mean_contraction"], 1)

    def test_max_path_distance(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .basal_dendrite(1, 0, 0)
                        .axon(1, -1, 0).up()
                        .basal_dendrite(2, 0, 0)
                            .basal_dendrite(3, 0, 0).up()
                            .basal_dendrite(2, 1, 0).up(3)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                            .apical_dendrite(-1, 2, 0).up()
                            .apical_dendrite(1, 2, 0)
                                .apical_dendrite(1, 3, 0)
                .build()
        )


        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(max_path_distance, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.max_path_distance"], 4)
        self.assertEqual(feature_extraction_run.results["axon.max_path_distance"], 2)
        self.assertEqual(feature_extraction_run.results["dendrite.max_path_distance"], 4)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.max_path_distance"], 3)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.max_path_distance"], 4)
