import unittest

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    AXON, APICAL_DENDRITE, BASAL_DENDRITE, SOMA
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE_SPECIALIZATIONS
from neuron_morphology.features.statistics import moments as mo
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
                # Axon node [100, 125, 150, 200, 200]
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 125,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 2,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 150,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 3,
                    "parent_id": 2,
                    "type": AXON,
                    "x": 0,
                    "y": 200,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 200,
                    "z": 0,
                    "radius": 3
                },
                # Basal node [100, 75, 50, 50]
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
                {
                    "id": 14,
                    "parent_id": 13,
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

        self.moment_features = nested_specialize(
            mo.moments,
            [COORD_TYPE_SPECIALIZATIONS, NEURITE_SPECIALIZATIONS])

    def extract(self, feature):
        extractor = FeatureExtractor([feature])
        return (
            extractor.extract(self.one_dim_neuron_data).results
        )

    def test_axon_compartment_moments(self):
        expected_axon_compartment_moments = {
            'mean': np.asarray([0.0, 115.625, 0.0]),
            'std': np.asarray([0.0, 52.504252, 0.0]),
            'var': np.asarray([0.0, 2756.696429, 0.0]),
            'skew': np.asarray([0.0, 0.38177086, 0.0]),
            'kurt': np.asarray([-3, -1.05489354, -3]),
        }
        axon_compartment_moments = \
            self.extract(self.moment_features)["axon.compartment.moments"]

        for key in axon_compartment_moments.keys():
            self.assertIsNone(np.testing.assert_allclose(
                axon_compartment_moments[key],
                expected_axon_compartment_moments[key]))
