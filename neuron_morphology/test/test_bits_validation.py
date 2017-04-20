from neuron_morphology import node
from neuron_morphology import morphology
from neuron_morphology.validation import bits_validation as bv
from neuron_morphology.validation.errors import InvalidMorphology
from neuron_morphology.test.validation_test_case import ValidationTestCase
import unittest
from mock import patch


class TestBitsValidationFunctions(ValidationTestCase):
    """ Tests the functions in bits_validation.py """

    @patch("neuron_morphology.validation.validators", [bv])
    def test_independent_axon_with_less_than_three_nodes_valid(self):
        morphology.Morphology([node.Node(1, 1, 3181.11, 2898.45, 87.1713, 2.0, -1)
                              , node.Node(2, 2, 3188.34, 2891.57, 88.9906, 2.0, -1)
                              , node.Node(3, 2, 3198.34, 2888.57, 89.9906, 2.0, 2)
                              , node.Node(4, 2, 3198.34, 2888.57, 89.9906, 2.0, 2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [bv])
    def test_independent_axon_with_less_than_three_nodes_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, -1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "There is an independent axon with less than 3 nodes", [3])

    @patch("neuron_morphology.validation.validators", [bv])
    def test_type3_traceable_back_to_soma_valid(self):
        morphology.Morphology([node.Node(1, 1, 3181.11, 2898.45, 87.1713, 2.0, -1)
                              , node.Node(2, 2, 3188.34, 2891.57, 88.9906, 2.0, 1)
                              , node.Node(3, 3, 3198.34, 2888.57, 89.9906, 2.0, 2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [bv])
    def test_type3_traceable_back_to_soma_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 3, 6725.2098, 5890.6503, 76.0, 2.0, -1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "must be traceable back to the soma", [3])

    @patch("neuron_morphology.validation.validators", [bv])
    def test_type4_traceable_back_to_soma_valid(self):
        morphology.Morphology([node.Node(1, 1, 3181.11, 2898.45, 87.1713, 2.0, -1)
                              , node.Node(2, 2, 3188.34, 2891.57, 88.9906, 2.0, 1)
                              , node.Node(3, 4, 3198.34, 2888.57, 89.9906, 2.0, 1)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [bv])
    def test_type4_traceable_back_to_soma_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 4, 6725.2098, 5890.6503, 76.0, 2.0, -1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "must be traceable back to the soma", [3])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBitsValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)