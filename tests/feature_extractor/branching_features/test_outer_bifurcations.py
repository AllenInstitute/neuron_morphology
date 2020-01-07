import unittest

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    AXON, APICAL_DENDRITE, BASAL_DENDRITE, SOMA
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.branching import outer_bifurcations as ob
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.feature_specialization import (
    AxonSpec,
    ApicalDendriteSpec,
    BasalDendriteSpec,
)
from neuron_morphology.feature_extractor.marked_feature import specialize


class TestOuterBifurcations(unittest.TestCase):

    def setUp(self):

        self.one_dim_neuron = Morphology([
                {
                    "id": 0,
                    "parent_id": -1,
                    "type": SOMA,
                    "x": 0,
                    "y": 0,
                    "z": 100,
                    "radius": 1
                },
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 101,
                    "radius": 1
                },
                {
                    "id": 2,
                    "parent_id": 0,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 102,
                    "radius": 1
                },
                { # bifurcates and is within 120
                    "id": 3,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 110,
                    "radius": 1
                },                
                { # This is the farthest node from the root
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 140,
                    "radius": 1 
                },                
                { # bifurcates, and is beyond 120
                    "id": 5,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 130,
                    "radius": 1 
                },                
                {
                    "id": 6,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 135,
                    "radius": 1 
                },       
                {
                    "id": 7,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 136,
                    "radius": 1 
                },     
                { # bifurcates and is beyond 120
                    "id": 8,
                    "parent_id": 2,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 125,
                    "radius": 1 
                },
                {
                    "id": 9,
                    "parent_id": 8,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 126,
                    "radius": 1 
                },
                {
                    "id": 10,
                    "parent_id": 8,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 127,
                    "radius": 1 
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.one_dim_neuron_data = Data(self.one_dim_neuron)

        self.neurite_features = specialize(
            ob.num_outer_bifurcations,
            {AxonSpec, ApicalDendriteSpec, BasalDendriteSpec}
        )

    def extract(self, feature):
        extractor = FeatureExtractor([feature])
        return (
            extractor.extract(self.one_dim_neuron_data)
                .results
        )

    def test_calculate_outer_bifs(self):
        self.assertEqual(ob.calculate_outer_bifs(
            self.one_dim_neuron,
            self.one_dim_neuron.get_root(),
            None
        ), 2)


    def test_num_outer_bifurcations(self):
        self.assertEqual(
            self.extract(ob.num_outer_bifurcations)["num_outer_bifurcations"],
            2
        )

    def test_apical_num_outer_bifurcations(self):
        self.assertEqual(
            self.extract(self.neurite_features)["apical_dendrite.num_outer_bifurcations"],
            1
        )

    def test_axon_num_outer_bifurcations(self):
        self.assertEqual(
            self.extract(self.neurite_features)["axon.num_outer_bifurcations"],
            1
        )

    def test_basal_num_outer_bifurcations(self):
        # skipped due to no basal dendrite nodes
        self.assertNotIn(
            "basal_dendrite.num_outer_bifurcations",
            self.extract(self.neurite_features),
        )