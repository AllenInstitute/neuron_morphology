import unittest

from neuron_morphology.constants import *
from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor # for individual cell features
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.marked_feature import (
    specialize
)
from neuron_morphology.feature_extractor.feature_specialization import (
    BasalDendriteSpec, AxonSpec
)
from neuron_morphology.features.soma import (
    calculate_stem_exit_and_distance
)
from tests.objects import test_node


class TestStemExit(unittest.TestCase):

    def test_stem_exit_with_type(self):

        nodes = [
            test_node(id=1, type=SOMA, x=0, y=0, z=0, radius=10, parent_node_id=-1),
            test_node(id=2, type=BASAL_DENDRITE, x=10, y=0, z=0, radius=2, parent_node_id=1),
            test_node(id=3, type=BASAL_DENDRITE, x=20, y=0, z=0, radius=2, parent_node_id=2),
            test_node(id=4, type=AXON, x=30, y=0, z=0, radius=0.5, parent_node_id=2),
            test_node(id=5, type=AXON, x=40, y=0, z=0, radius=0.5, parent_node_id=4),
            test_node(id=6, type=BASAL_DENDRITE, x=0, y=-10, z=0, radius=2, parent_node_id=1),
        ]

        for node in nodes:
            node['parent'] = int(node['parent'])
            node['id'] = int(node['id'])
            node['type'] = int(node['type'])

        morphology = Morphology(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'])


        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(calculate_stem_exit_and_distance, [BasalDendriteSpec, AxonSpec])])
        feature_extraction_run = fe.extract(cell_data)

        axon_results = feature_extraction_run.results["axon.calculate_stem_exit_and_distance"]
        basal_results = feature_extraction_run.results["basal_dendrite.calculate_stem_exit_and_distance"]
        self.assertEqual(axon_results[0][0], 0.5)
        self.assertEqual(axon_results[0][1], 30.0)
        self.assertEqual(basal_results[0][0], 0.5)
        self.assertEqual(basal_results[0][1], 0)
        self.assertEqual(basal_results[1][0], 1)
        self.assertEqual(basal_results[1][1], 0)
