from neuron_morphology.validation.result import NodeValidationError
from neuron_morphology.validation.result import MarkerValidationError
import unittest


class ValidationTestCase(unittest.TestCase):
    def assertNodeErrors(self, validation_errors, expected_message_fragment, expected_invalid_node_ids):
        matching_node_ids = [e.node_ids for e in validation_errors if expected_message_fragment in e.message]
        self.assertEqual(expected_invalid_node_ids, matching_node_ids,
                         ("Expected nodes %s to be reported invalid with a message containing:\n '%s'. "
                          + "\nActual errors:\n%s") %
                         (expected_invalid_node_ids, expected_message_fragment,
                          '\n'.join(map(NodeValidationError.__str__, validation_errors))))

    def assertMarkerErrors(self, validation_errors, expected_message_fragment, expected_invalid_markers):
        matching_markers = [e.marker for e in validation_errors if expected_message_fragment in e.message]
        self.assertEqual(expected_invalid_markers, matching_markers,
                         ("Expected markers %s to be reported invalid with a message containing:\n '%s'. "
                          + "\nActual errors:\n%s") %
                         (expected_invalid_markers, expected_message_fragment,
                          '\n'.join(map(MarkerValidationError.__str__, validation_errors))))
