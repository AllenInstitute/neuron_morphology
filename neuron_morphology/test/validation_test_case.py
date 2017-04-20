from neuron_morphology.validation.errors import ValidationError
import unittest


class ValidationTestCase(unittest.TestCase):
    def assertNodeErrors(self, validation_errors, expected_message_fragment, expected_invalid_node_ids):
        matching_node_ids = [e.node_id for e in validation_errors if expected_message_fragment in e.message]
        self.assertItemsEqual(expected_invalid_node_ids, matching_node_ids,
                              ("Expected nodes %s to be reported invalid with a message containing:\n '%s'. "
                              + "\nActual errors:\n%s") %
                              (expected_invalid_node_ids, expected_message_fragment,
                               '\n'.join(map(ValidationError.__str__, validation_errors))))
