import unittest

import numpy as np

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    AXON, APICAL_DENDRITE, BASAL_DENDRITE, SOMA
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE_SPECIALIZATIONS
from neuron_morphology.features.statistics import moments_along_max_distance_projection as mo_proj
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS)
from neuron_morphology.feature_extractor.marked_feature import nested_specialize


class TestMaxDistProjMoment(unittest.TestCase):

    def setUp(self):

        # Create an axon that extends positively with bifurcations
        self.one_dim_neuron = Morphology([
                {
                    "id": 0,
                    "parent_id": -1,
                    "type": SOMA,
                    "x": 0,
                    "y": 0,
                    "z": 0,
                    "radius": 10
                },
                # Axon node and bifurcations at [25, 50,75,100]
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 25,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 2,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 25,
                    "y": 0,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 3,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 50,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 50,
                    "y": 0,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 5,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 75,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 6,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 75,
                    "y": 0,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 7,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 0,
                    "y": 100,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 8,
                    "parent_id": 7,
                    "type": AXON,
                    "x": 100,
                    "y": 0,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 9,
                    "parent_id": 7,
                    "type": AXON,
                    "x": -100,
                    "y": 0,
                    "z": 0,
                    "radius": 3
                },
                # Basal node [100, 75, 50, 50]
                {
                    "id": 10,
                    "parent_id": 0,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": -100,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 11,
                    "parent_id": 11,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": -75,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 12,
                    "parent_id": 12,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": -50,
                    "z": 0,
                    "radius": 3
                },
                {
                    "id": 13,
                    "parent_id": 13,
                    "type": BASAL_DENDRITE,
                    "x": 0,
                    "y": -50,
                    "z": 0,
                    "radius": 3
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.one_dim_neuron_data = Data(self.one_dim_neuron)

        self.moment_features = nested_specialize(
            mo_proj.moments_along_max_distance_projection,
            [COORD_TYPE_SPECIALIZATIONS, NEURITE_SPECIALIZATIONS])

    def extract(self, feature):
        extractor = FeatureExtractor([feature])
        return (
            extractor.extract(self.one_dim_neuron_data).results
        )

    def test_axon_compartment_moments(self):
        expected_axon_compartment_moments = {
            'mean': 0.625,
            'std': 0.2795084971874737,
            'var': 0.10416666666666667,
            'skew': 0.0,
            'kurt': -1.36
        }
        axon_compartment_proj_moments = \
            self.extract(self.moment_features)["axon.bifurcation.moments_along_max_distance_projection"]

        for key in axon_compartment_proj_moments.keys():
            self.assertIsNone(np.testing.assert_allclose(
                axon_compartment_proj_moments[key],
                expected_axon_compartment_moments[key]))

