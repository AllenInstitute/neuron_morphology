from neuron_morphology import validation as validation
from neuron_morphology import node
from neuron_morphology import morphology
from neuron_morphology.validation.errors import InvalidMorphology
from neuron_morphology.validation import type_validation as tv
import unittest
from mock import patch


class TestTypeValidationFunctions(unittest.TestCase):
    """ Tests the functions in type_validation.py """

    @patch("neuron_morphology.validation.validators", [tv])
    def test_validate_expected_type_valid(self):
        values = node.Node(2, 3, 6725.2098, 5890.6503, 76.0, 2.0, 1)
        errors = validation.type_validation.validate_expected_types(values)
        self.assertEqual(len(errors), 0)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_validate_expected_type_invalid(self):
        values = node.Node(2, 5, 6725.2098, 5890.6503, 76.0, 2.0, 1)
        errors = validation.type_validation.validate_expected_types(values)
        self.assertEqual(len(errors), 1)
        self.assertIn("Node type needs to be one of these values:", errors[0].message)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type1_node_with_valid_parent(self):
        morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                              , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                              , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type1_node_with_invalid_parent(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 1, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)
                                  , node.Node(4, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 3)
            self.assertIn("Type 1 can only have a parent of the following types:", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 2)
            self.assertEqual(e.validation_errors[1].node_id, 1)
            self.assertEqual(e.validation_errors[2].node_id, 2)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type2_node_with_valid_parent_type(self):
        morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                              , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                              , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type2_node_with_invalid_parent_type(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 4, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 1)
            self.assertIn("Type 2 can only have a parent of the following types:", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 3)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type3_node_with_valid_parent_type(self):
        morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                              , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                              , node.Node(3, 3, 6728.1399, 5881.1399, 76.0004, 2.0, 1)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type3_node_with_invalid_parent_type(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 3, 6728.1399, 5881.1399, 76.0004, 2.0, 2)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 1)
            self.assertIn("Type 3 can only have a parent of the following types:", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 3)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type4_node_with_valid_parent_type(self):
        morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                              , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                              , node.Node(3, 3, 6728.1399, 5881.1399, 76.0004, 2.0, 1)
                              , node.Node(4, 4, 6728.1399, 5881.1399, 76.0004, 2.0, 1)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_type4_node_with_invalid_parent_type(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 3, 6728.1399, 5881.1399, 76.0004, 2.0, 1)
                                  , node.Node(4, 4, 6728.1399, 5881.1399, 76.0004, 2.0, 3)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 1)
            self.assertIn("Type 4 can only have a parent of the following types:", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 4)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_number_of_type1_nodes_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 2)
            self.assertIn("There can only be one node of type 1", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 1)
            self.assertEqual(e.validation_errors[1].node_id, 2)

    @patch("neuron_morphology.validation.validators", [tv])
    def test_number_of_type4_with_parent_of_type1_invalid(self):
        try:
            morphology.Morphology([node.Node(1, 1, 6725.2098, 5890.6503, 76.0, 2.0, -1)
                                  , node.Node(2, 2, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(3, 2, 6725.2098, 5890.6503, 76.0, 2.0, 2)
                                  , node.Node(4, 4, 6725.2098, 5890.6503, 76.0, 2.0, 1)
                                  , node.Node(5, 4, 6725.2098, 5890.6503, 76.0, 2.0, 1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertEqual(len(e.validation_errors), 2)
            self.assertIn("Nodes of type 4 can only have 1 parent of type 1", e.validation_errors[0].message)
            self.assertEqual(e.validation_errors[0].node_id, 4)
            self.assertEqual(e.validation_errors[1].node_id, 5)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTypeValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
