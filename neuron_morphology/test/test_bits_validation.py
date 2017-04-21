from neuron_morphology.test.data import test_node
from neuron_morphology import morphology
from neuron_morphology.validation import bits_validation as bv
from neuron_morphology.validation.errors import InvalidMorphology
from neuron_morphology.test.validation_test_case import ValidationTestCase
from neuron_morphology.constants import *
import unittest
from mock import patch


class TestBitsValidationFunctions(ValidationTestCase):
    """ Tests the functions in bits_validation.py """

    @patch("neuron_morphology.validation.validators", [bv])
    def test_independent_axon_with_less_than_three_nodes_valid(self):
        morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                              , test_node(id=2, type=AXON, parent_node_id=-1)
                              , test_node(id=3, type=AXON, parent_node_id=2)
                              , test_node(id=4, type=AXON, parent_node_id=2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [bv])
    def test_independent_axon_with_less_than_three_nodes_invalid(self):
        try:
            morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                  , test_node(id=2, type=AXON, parent_node_id=1)
                                  , test_node(id=3, type=AXON, parent_node_id=-1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "There is an independent axon with less than 3 nodes", [3])

    @patch("neuron_morphology.validation.validators", [bv])
    def test_basal_dendrite_traceable_back_to_soma_valid(self):
        morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                              , test_node(id=2, type=AXON, parent_node_id=1)
                              , test_node(id=3, type=BASAL_DENDRITE, parent_node_id=2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [bv])
    def test_basal_dendrite_traceable_back_to_soma_invalid(self):
        try:
            morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                  , test_node(id=2, type=AXON, parent_node_id=1)
                                  , test_node(id=3, type=BASAL_DENDRITE, parent_node_id=-1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "must be traceable back to the soma", [3])

    @patch("neuron_morphology.validation.validators", [bv])
    def test_apical_dendrite_traceable_back_to_soma_valid(self):
        morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                              , test_node(id=2, type=AXON, parent_node_id=1)
                              , test_node(id=3, type=APICAL_DENDRITE, parent_node_id=1)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [bv])
    def test_apical_dendrite_traceable_back_to_soma_invalid(self):
        try:
            morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                  , test_node(id=2, type=AXON, parent_node_id=1)
                                  , test_node(id=3, type=APICAL_DENDRITE, parent_node_id=-1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "must be traceable back to the soma", [3])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBitsValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
