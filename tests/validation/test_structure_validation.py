from tests.objects import test_node, test_tree
from neuron_morphology.validation.result import InvalidMorphology
from neuron_morphology.validation import structure_validation as sv
from tests.validation.validation_test_case import ValidationTestCase
from neuron_morphology.constants import *
import unittest
from mock import patch


class TestStructureValidationFunctions(ValidationTestCase):
    """ Tests the functions in structure_validation.py """

    @patch("neuron_morphology.validation.swc_validators", [sv])
    def test_children_nodes_appear_before_parent_nodes_valid(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                 test_node(id=2, type=APICAL_DENDRITE, parent_node_id=1)]

        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [sv])
    def test_children_nodes_appear_before_parent_nodes_not_valid(self):
        try:
            nodes = [test_node(id=1, type=AXON, parent_node_id=2),
                     test_node(id=2, type=SOMA, parent_node_id=-1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Child node needs to come before parent node",
                                  [[1]])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStructureValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
