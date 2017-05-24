from neuron_morphology.test.data import test_node
from neuron_morphology import morphology
from neuron_morphology.validation import resample_validation as rev
from neuron_morphology.validation.result import InvalidMorphology
from neuron_morphology.test.validation_test_case import ValidationTestCase
from neuron_morphology.constants import *
import unittest
from mock import patch


class TestResampleValidationFunctions(ValidationTestCase):
    """ Tests the functions in resample_validation.py """

    @patch("neuron_morphology.validation.swc_validators", [rev])
    def test_distance_between_connected_nodes_valid(self):
        morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                              , test_node(id=2, type=AXON, x=3188.34, y=2891.57, z=88.9906, parent_node_id=1)
                              , test_node(id=3, type=AXON, x=3198.34, y=2888.57, z=89.9906, parent_node_id=2)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rev])
    def test_distance_between_connected_nodes_invalid(self):
        try:
            morphology.Morphology([test_node(id=1, type=SOMA, parent_node_id=-1)
                                  , test_node(id=2, type=AXON, x=6725.2098, y=5890.6503, z=76.0, parent_node_id=1)
                                  , test_node(id=3, type=AXON, x=0, y=0, z=0, parent_node_id=2)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "The distance between two nodes should be less than 50px"
                                  , [[2, 3]])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestResampleValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
