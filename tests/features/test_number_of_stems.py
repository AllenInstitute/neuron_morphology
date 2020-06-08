import unittest

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.marked_feature import (
    specialize
)
from neuron_morphology.feature_extractor.feature_specialization import (
    BasalDendriteSpec
)
from neuron_morphology.features.soma import (
    calculate_number_of_stems
)

class TestNumberOfStems(unittest.TestCase):

    def test_number_of_stems_with_type(self):

        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .axon().up()
                    .basal_dendrite().up()
                    .basal_dendrite()
                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(calculate_number_of_stems, [BasalDendriteSpec])])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(
            feature_extraction_run.results["basal_dendrite.calculate_number_of_stems"],
            2
        )


