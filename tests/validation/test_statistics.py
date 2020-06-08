from tests.objects import test_node
from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import *
from neuron_morphology.validation.morphology_statistics import \
    morphology_statistics
import unittest
from mock import patch


class TestMorphologyStatistics(unittest.TestCase):
    """ Tests the functions in bits_statistics.py """

    def test_independent_axon_count_zero(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=1)]
        test_morphology = Morphology(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'])
        test_morphology.validate(strict=False)

        stat = morphology_statistics(test_morphology)
        self.assertEqual(stat["Number of Independent Axons"], 0)

    def test_independent_axon_count_one(self):

        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=-1)]
        test_morphology = Morphology(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'])
        test_morphology.validate(strict=False)

        stat = morphology_statistics(test_morphology)
        self.assertEqual(stat["Number of Independent Axons"], 1)

    def test_independent_axon_count_five(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=-1),
                 test_node(id=3, type=AXON, parent_node_id=-1), test_node(id=4, type=AXON, parent_node_id=-1),
                 test_node(id=5, type=AXON, parent_node_id=-1), test_node(id=6, type=AXON, parent_node_id=-1)]
        test_morphology = Morphology(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'])
        test_morphology.validate(strict=False)

        stat = morphology_statistics(test_morphology)
        self.assertEqual(stat["Number of Independent Axons"], 5)