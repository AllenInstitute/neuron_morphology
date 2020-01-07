import unittest

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    AXON, APICAL_DENDRITE, BASAL_DENDRITE, SOMA
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE_SPECIALIZATIONS
from neuron_morphology.features import dimension as di
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS)
from neuron_morphology.feature_extractor.marked_feature import nested_specialize


class TestOverlap(unittest.TestCase):

    def setUp(self):

        # Create an axon that extends positively,
        # and a basal dendrite that extends negatively
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
                    "x": 0,
                    "y": 175,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 5,
                    "parent_id": 4,
                    "type": AXON,
                    "x": 0,
                    "y": 200,
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
                    "x": 0,
                    "y": 50,
                    "z": 0,
                    "radius": 3
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.one_dim_neuron_data = Data(self.one_dim_neuron)

        self.dimension_features = nested_specialize(
            di.dimension,
            [COORD_TYPE_SPECIALIZATIONS, NEURITE_SPECIALIZATIONS])

    def extract(self, feature):
        extractor = FeatureExtractor([feature])
        return (
            extractor.extract(self.one_dim_neuron_data).results
        )

    def test_all_neurites_node_dimension(self):
        expected_all_neurites_node_dimension = {
            'width': 0.0,
            'height': 150.0,
            'depth': 0.0,
            'min_xyz': np.asarray([0.0, -50.0, 0.0]),
            'max_xyz': np.asarray([0.0, 100.0, 0.0]),
            'bias_xyz': np.asarray([0.0, 50.0, 0.0])
        }
        all_neurites_node_dimension = \
            self.extract(self.dimension_features)["all_neurites.node.dimension"]
        for key in all_neurites_node_dimension.keys():
            self.assertIsNone(np.testing.assert_allclose(
                all_neurites_node_dimension[key],
                expected_all_neurites_node_dimension[key]))
