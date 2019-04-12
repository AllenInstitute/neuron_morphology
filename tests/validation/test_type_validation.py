from tests.objects import test_node, test_tree
from neuron_morphology.validation.result import InvalidMorphology
from neuron_morphology.validation import type_validation as tv
from tests.validation.validation_test_case import ValidationTestCase
from neuron_morphology.constants import *
import unittest
from mock import patch


class TestTypeValidationFunctions(ValidationTestCase):
    """ Tests the functions in type_validation.py """

    def test_validate_expected_type_valid(self):
        for node_type in [AXON, BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA), test_node(id=2, type=node_type, parent_node_id=1)]
            errors = tv.validate_expected_types(test_tree(nodes))
            self.assertEqual(len(errors), 0)

    def test_validate_expected_type_invalid(self):
        nodes = [test_node(type=5)]
        errors = tv.validate_expected_types(test_tree(nodes))
        self.assertNodeErrors(errors, "Node type needs to be one of these values:", [[1]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_soma_node_with_valid_parent(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_soma_node_with_invalid_parent(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=SOMA, parent_node_id=1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Type 1 can only have a parent of the following types:", [[2]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_axon_node_with_valid_parent_type(self):
        for node_type in [SOMA, AXON]:
            nodes = [test_node(id=1, type=node_type, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=1)]
            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_axon_node_with_invalid_parent_type(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=APICAL_DENDRITE, parent_node_id=1),
                     test_node(id=3, type=AXON, parent_node_id=2)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Type 2 can only have a parent of the following types:", [[3]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_basal_dendrite_node_with_valid_parent_type(self):
        for node_type in [SOMA]:
            nodes = [test_node(id=1, type=node_type, parent_node_id=-1),
                     test_node(id=2, type=BASAL_DENDRITE, parent_node_id=1)]
            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_basal_dendrite_node_with_invalid_parent_type(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=AXON, parent_node_id=1),
                     test_node(id=3, type=BASAL_DENDRITE, parent_node_id=2)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Type 3 can only have a parent of the following types:", [[3]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_basal_dendrite_node_with_invalid_parent_type_independent(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=1),
                     test_node(id=3, type=BASAL_DENDRITE, parent_node_id=-1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Type 3 can only have a parent of the following types:", [[3]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_apical_dendrite_node_with_invalid_parent_type_independent(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=1),
                     test_node(id=3, type=APICAL_DENDRITE, parent_node_id=-1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Type 4 can only have a parent of the following types:", [[3]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_apical_dendrite_node_with_valid_parent_type(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=APICAL_DENDRITE, parent_node_id=1)]
        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_apical_node_with_invalid_parent_type(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=AXON, parent_node_id=1),
                     test_node(id=3, type=BASAL_DENDRITE, parent_node_id=1),
                     test_node(id=4, type=APICAL_DENDRITE, parent_node_id=3)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Type 4 can only have a parent of the following types:", [[4]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_number_of_soma_nodes_invalid(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=SOMA, parent_node_id=-1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "The morphology needs to have one soma node", [[1], [2]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_number_of_apical_dendrite_with_parent_of_soma_invalid(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=APICAL_DENDRITE, parent_node_id=1),
                     test_node(id=3, type=APICAL_DENDRITE, parent_node_id=1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Nodes of type 4 can only have 1 parent of type 1", [[2], [3]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_immediate_child_of_soma_doesnt_more_than_one_child(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                 test_node(id=2, type=APICAL_DENDRITE, parent_node_id=1),
                 test_node(id=3, type=APICAL_DENDRITE, parent_node_id=2),
                 test_node(id=4, type=APICAL_DENDRITE, parent_node_id=3),
                 test_node(id=5, type=APICAL_DENDRITE, parent_node_id=3)]
        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_immediate_child_of_soma_has_more_than_one_child(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=APICAL_DENDRITE, parent_node_id=1),
                     test_node(id=3, type=APICAL_DENDRITE, parent_node_id=2),
                     test_node(id=4, type=APICAL_DENDRITE, parent_node_id=2)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Immediate children of soma cannot branch", [[2]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_multiple_axon_initiation_points_not_valid(self):
        try:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=AXON, parent_node_id=1),
                     test_node(id=3, type=AXON, parent_node_id=1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Axon can only have one parent of type basal dendrite or soma",
                                  [[2], [3]])

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_multiple_axon_initiation_points_valid(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                 test_node(id=2, type=AXON, parent_node_id=1)]

        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [tv])
    def test_multiple_axon_initiation_points_valid_with_independent_axon(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                 test_node(id=2, type=AXON, parent_node_id=1),
                 test_node(id=3, type=AXON, parent_node_id=-1)]

        test_tree(nodes, strict_validation=True)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTypeValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
