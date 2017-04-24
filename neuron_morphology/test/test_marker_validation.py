from neuron_morphology.validation.errors import InvalidMarkerFile
from neuron_morphology import swc
from neuron_morphology.test.data import test_marker
from neuron_morphology.validation import marker_validation as mv
from neuron_morphology.test.validation_test_case import ValidationTestCase
from neuron_morphology.constants import *
import unittest
from mock import patch


class TestMarkerValidationFunctions(ValidationTestCase):
    """ Tests the functions in marker_validation.py """

    def test_validate_expected_name_valid(self):
        for marker_name in [CUT_DENDRITE, NO_RECONSTRUCTION, TYPE_30]:
            errors = mv.validate_expected_name([test_marker(name=marker_name)])
            self.assertEqual(len(errors), 0)

    def test_validate_expected_name_invalid(self):
        errors = mv.validate_expected_name([test_marker(name=5)])
        self.assertMarkerErrors(errors, "Marker name needs to be one of these values:", [test_marker(name=5)])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarkerValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
