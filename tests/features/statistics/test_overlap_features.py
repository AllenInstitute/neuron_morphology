import unittest

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    AXON, APICAL_DENDRITE, BASAL_DENDRITE, SOMA
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics import overlap
# from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
# from neuron_morphology.feature_extractor.feature_specialization import (
#     AxonSpec,
#     ApicalDendriteSpec,
#     BasalDendriteSpec,
# )


class TestOverlap(unittest.TestCase):

    def setUp(self):

        # Create an Axon that extends y 100 to 120
        # and Basal Dendrite that extends y 100 to 110 and 100 to 80
        # So that 3/4 axon nodes overlap, 1/4 are above basal
        # and that 3/6 basal are below, and 3/6 overlap
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
                # Axon y 100 to 150
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 101,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 2,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 102,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 3,
                    "parent_id": 2,
                    "type": AXON,
                    "x": 0,
                    "y": 110,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 120,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 11,
                    "parent_id": 0,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 101,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 12,
                    "parent_id": 11,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 102,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 13,
                    "parent_id": 12,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 110,
                    "z": 0,
                    "radius": 3
                },
                # Basal Dendrite y 100 to 80
                {
                    "id": 14,
                    "parent_id": 12,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 99,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 15,
                    "parent_id": 14,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 90,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 16,
                    "parent_id": 15,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": 80,
                    "z": 0,
                    "radius": 3
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

    # def test_calculate_overlap(self):
    #     pass

    def test_calculate_overlap_of_all_node_sets(self):

        expected_overlap_features = {
            'above_APICAL_DENDRITE': -1,
            'above_AXON': 0.0,
            'above_BASAL_DENDRITE': 0.25,
            'above_DENDRITE': 0.25,
            'below_APICAL_DENDRITE': -1,
            'below_AXON': 0.0,
            'below_BASAL_DENDRITE': 0.0,
            'below_DENDRITE': 0.0,
            'overlap_APICAL_DENDRITE': -1,
            'overlap_AXON': 1.0,
            'overlap_BASAL_DENDRITE': 0.75,
            'overlap_DENDRITE': 0.75,
        }
        overlap_features = overlap.calculate_overlap_of_all_node_sets(
            self.one_dim_neuron,
            node_types=[AXON]
        )
        self.maxDiff = None
        print(overlap_features)
        self.assertDictEqual(overlap_features, expected_overlap_features)
