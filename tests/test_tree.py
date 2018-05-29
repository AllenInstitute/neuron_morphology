import unittest
import os
import allensdk.neuron_morphology.swc_io as swc
import allensdk.neuron_morphology.constants as constants
from allensdk.neuron_morphology.tree import Tree


class TestTree(unittest.TestCase):

    data_dir = os.path.join(os.path.dirname(__file__), 'data')
    swc_file = os.path.join(data_dir, 'test_swc.swc')

    def test_get_root(self):

        tree = swc.tree_from_swc(self.swc_file)
        expected_root = {'id': 1, 'type': 1, 'x': 1220.9912, 'y': 610.7816, 'z': 30.8, 'radius': 7.7811, 'parent': -1}
        self.assertEqual(expected_root, tree.get_root())

    # def test_get_node_by_type(self):
    #
    #     tree = swc.tree_from_swc(self.swc_file)
    #     # print(len(tree.get_node_by_type(constants.AXON)))
    #     print(tree)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTree)
    unittest.TextTestRunner(verbosity=5).run(suite)
