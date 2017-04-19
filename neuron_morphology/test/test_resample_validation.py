from neuron_morphology import validation as validation
from neuron_morphology import node
from neuron_morphology import morphology
from neuron_morphology.validation.errors import InvalidMorphology
import unittest
from mock import patch


class TestResampleValidationFunctions(unittest.TestCase):
    """ Tests the functions in resample_validation.py """

    @patch("neuron_morphology.validation", new=validation.resample_validation)
    def test_distance_between_connected_nodes_valid(self):
        morphology.Morphology([node.Node(1, 1, 3181.11, 2898.45, 87.1713, 2.0, -1)
                              , node.Node(2, 2, 3188.34, 2891.57, 88.9906, 2.0, 1)
                              , node.Node(3, 2, 3198.34, 2888.57, 89.9906, 2.0, 2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation", new=validation.resample_validation)
    def test_distance_between_connected_nodes_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                      , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                      , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 2)
            self.assertIn("The distance between two nodes should be approximately 10px", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 1)
            self.assertEqual(e.validation_errors[1].node_id, 2)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResampleValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
