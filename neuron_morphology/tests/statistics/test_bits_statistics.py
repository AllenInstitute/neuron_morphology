from neuron_morphology.tests.test_objects import test_node
from neuron_morphology.tree import Tree
from neuron_morphology.constants import *
from neuron_morphology.statistics import bits_statistics as bs
import unittest
from mock import patch


class TestBitsStatisticsFunctions(unittest.TestCase):
    """ Tests the functions in bits_statistics.py """

    @patch("neuron_morphology.statistics.swc_statistics", [bs])
    def test_independent_axon_count_zero(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=1)]
        test_morphology = Tree(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'],
                               strict_validation=False)

        stat = bs.statistics(test_morphology)
        self.assertEqual(stat["Number of Independent Axons"], 0)

    @patch("neuron_morphology.statistics.swc_statistics", [bs])
    def test_independent_axon_count_one(self):

        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=-1)]
        test_morphology = Tree(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'],
                               strict_validation=False)

        stat = bs.statistics(test_morphology)
        self.assertEqual(stat["Number of Independent Axons"], 1)

    @patch("neuron_morphology.statistics.swc_statistics", [bs])
    def test_independent_axon_count_five(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=-1),
                 test_node(id=3, type=AXON, parent_node_id=-1), test_node(id=4, type=AXON, parent_node_id=-1),
                 test_node(id=5, type=AXON, parent_node_id=-1), test_node(id=6, type=AXON, parent_node_id=-1)]
        test_morphology = Tree(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'],
                               strict_validation=False)

        stat = bs.statistics(test_morphology)
        self.assertEqual(stat["Number of Independent Axons"], 5)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBitsStatisticsFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
