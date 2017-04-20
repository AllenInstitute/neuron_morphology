from neuron_morphology import node
from neuron_morphology import morphology
from neuron_morphology.validation import resample_validation as rev
from neuron_morphology.validation.errors import InvalidMorphology
from neuron_morphology.test.validation_test_case import ValidationTestCase
import unittest
from mock import patch


class TestResampleValidationFunctions(ValidationTestCase):
    """ Tests the functions in resample_validation.py """

    @patch("neuron_morphology.validation.validators", [rev])
    def test_distance_between_connected_nodes_valid(self):
        morphology.Morphology([node.Node(1, 1, 3181.11, 2898.45, 87.1713, 2.0, -1)
                              , node.Node(2, 2, 3188.34, 2891.57, 88.9906, 2.0, 1)
                              , node.Node(3, 2, 3198.34, 2888.57, 89.9906, 2.0, 2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [rev])
    def test_distance_between_connected_nodes_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                      , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                      , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "The distance between two nodes should be approximately 10px"
                                  , [1, 2])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResampleValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
