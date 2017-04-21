from neuron_morphology import node
from neuron_morphology import morphology
from neuron_morphology.constants import *
from neuron_morphology.validation import radius_validation as rv
from neuron_morphology.validation.errors import InvalidMorphology
from neuron_morphology.test.data import test_node
from neuron_morphology.test.validation_test_case import ValidationTestCase
import unittest
from mock import patch


class TestRadiusValidationFunctions(ValidationTestCase):
    """ Tests the functions in radius_validation.py """

    def test_valid_radius_for_soma(self):
        for valid_radius in [35, 36, 100, 999]:
            errors = rv.validate_node_type_radius(test_node(type=SOMA, radius=valid_radius))
            self.assertEqual(len(errors), 0)

    def test_invalid_radius_for_soma(self):
        for invalid_radius in [-10, 0, 1, 34, 34.999]:
            errors = rv.validate_node_type_radius(test_node(type=SOMA, radius=invalid_radius))
            self.assertNodeErrors(errors, "The radius must be", [1])

    def test_any_radius_valid_for_axon(self):
        for valid_radius in [-10, 0, 3, float('inf')]:
            errors = rv.validate_node_type_radius(test_node(type=AXON, radius=valid_radius))
            self.assertEqual(len(errors), 0)

    def test_valid_radius_for_basal_dendrite(self):
        for valid_radius in [-1, 0, 10, 16, 29.999]:
            errors = rv.validate_node_type_radius(test_node(type=BASAL_DENDRITE, radius=valid_radius))
            self.assertEqual(len(errors), 0)

    def test_invalid_radius_for_basal_dendrite(self):
        for valid_radius in [30.002, 35, 40, 100, 1000]:
            errors = rv.validate_node_type_radius(test_node(type=BASAL_DENDRITE, radius=valid_radius))
            self.assertNodeErrors(errors, "The radius must be", [1])

    def test_valid_radius_for_apical_dendrite(self):
        for valid_radius in [-1, 0, 10, 16, 29.999]:
            errors = rv.validate_node_type_radius(test_node(type=APICAL_DENDRITE, radius=valid_radius))
            self.assertEqual(len(errors), 0)

    def test_invalid_radius_for_apical_dendrite(self):
        for valid_radius in [30.002, 35, 40, 100, 1000]:
            errors = rv.validate_node_type_radius(test_node(type=APICAL_DENDRITE, radius=valid_radius))
            self.assertNodeErrors(errors, "The radius must be", [1])

    @patch("neuron_morphology.validation.validators", [rv])
    def test_valid_radius_multiple_types(self):
        morphology.Morphology([test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1)
                              , test_node(id=2, type=AXON, radius=2.0, parent_node_id=-1)
                              , test_node(id=3, type=BASAL_DENDRITE, radius=2.0, parent_node_id=1)
                              , test_node(id=4, type=APICAL_DENDRITE, radius=2.0, parent_node_id=1)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [rv])
    def test_invalid_radius_multiple_types(self):
        try:
            morphology.Morphology([test_node(id=1, type=SOMA, radius=2.0, parent_node_id=-1)
                                  , test_node(id=2, type=AXON, radius=2.0, parent_node_id=-1)
                                  , test_node(id=3, type=BASAL_DENDRITE, radius=32.0, parent_node_id=1)
                                  , test_node(id=4, type=APICAL_DENDRITE, radius=32.0, parent_node_id=1)]
                                  , strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology, e:
            self.assertNodeErrors(e.validation_errors, "The radius must be", [1, 3, 4])

    @patch("neuron_morphology.validation.validators", [rv])
    def test_extreme_taper(self):
        morphology.Morphology([test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1)
                              , test_node(id=2, type=BASAL_DENDRITE, radius=2.0, parent_node_id=1)
                              , test_node(id=3, type=BASAL_DENDRITE, radius=2.0, parent_node_id=2)
                              , test_node(id=4, type=BASAL_DENDRITE, radius=2.0, parent_node_id=3)]
                              , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [rv])
    def test_absence_of_constriction_for_dendrite(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            morphology.Morphology([test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1)
                                  , test_node(id=2, type=dendrite_type, radius=12.0, parent_node_id=1)
                                  , test_node(id=3, type=dendrite_type, radius=11.0, parent_node_id=2)
                                  , test_node(id=4, type=dendrite_type, radius=10.0, parent_node_id=3)]
                                  , strict_validation=True)

    @patch("neuron_morphology.validation.validators", [rv])
    def test_existence_of_constriction_for_dendrite_one_child(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            try:
                morphology.Morphology([test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1)
                                      , test_node(id=2, type=dendrite_type, radius=10.0, parent_node_id=1)
                                      , test_node(id=3, type=dendrite_type, radius=11.0, parent_node_id=2)
                                      , test_node(id=4, type=dendrite_type, radius=12.0, parent_node_id=3)]
                                      , strict_validation=True)
                self.fail("Morphology should have been rejected.")
            except InvalidMorphology, e:
                self.assertNodeErrors(e.validation_errors, "Constriction: The radius of types 3 and 4 should not be"
                                                           "smaller than the radius of their immediate child", [2, 3])

    @patch("neuron_morphology.validation.validators", [rv])
    def test_existence_of_constriction_for_dendrite_multiple_children(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            try:
                morphology.Morphology([test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1)
                                      , test_node(id=2, type=dendrite_type, radius=10.0, parent_node_id=1)
                                      , test_node(id=3, type=dendrite_type, radius=11.0, parent_node_id=2)
                                      , test_node(id=4, type=dendrite_type, radius=9.0, parent_node_id=2)]
                                      , strict_validation=True)
                self.fail("Morphology should have been rejected.")
            except InvalidMorphology, e:
                self.assertNodeErrors(e.validation_errors, "Constriction: The radius of types 3 and 4 should not be"
                                                           "smaller than the radius of their immediate child", [2])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRadiusValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
