from tests.objects import test_marker, test_node, test_tree
from neuron_morphology.validation import marker_validation as mv
from tests.validation.validation_test_case import ValidationTestCase
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
        self.assertMarkerErrors(errors, "Marker name needs to be one of these values:",
                                [[{'x': 0, 'y': 0, 'z': 0, 'name': 5}]])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_cut_dendrite_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
            mv.validate([test_marker(x=0, y=0, z=0, name=CUT_DENDRITE)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_cut_dendrite_invalid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
            errors = mv.validate([test_marker(x=1, y=0, z=0, name=CUT_DENDRITE),
                                  test_marker(x=1, y=0, z=0, name=TYPE_30)], test_tree(nodes))

            self.assertMarkerErrors(errors, "Coordinates for each dendrite (type 10) needs to correspond to "
                                            "a tip of a dendrite type (type 3 or 4) in the related morphology",
                                    [[{'x': 1, 'y': 0, 'z': 0, 'name': CUT_DENDRITE}]])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_multiple_cut_dendrite_invalid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
            errors = mv.validate([test_marker(x=1, y=0, z=0, name=CUT_DENDRITE),
                                  test_marker(x=1, y=0, z=0, name=TYPE_30)], test_tree(nodes))

            self.assertMarkerErrors(errors, "Coordinates for each dendrite (type 10) needs to correspond to "
                                            "a tip of a dendrite type (type 3 or 4) in the related morphology",
                                    [[{'x': 1, 'y': 0, 'z': 0, 'name': CUT_DENDRITE}]])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_axon_tips_no_reconstruction_invalid(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                 test_node(id=2, type=AXON, x=0, y=0, z=0, parent_node_id=1)]
        errors = mv.validate([test_marker(x=1, y=0, z=0, name=NO_RECONSTRUCTION),
                              test_marker(x=1, y=0, z=0, name=TYPE_30)], test_tree(nodes))

        self.assertMarkerErrors(errors, "Coordinates for each axon (type 20) needs to correspond to "
                                        "a tip of an axon type (type 2) in the related morphology",
                                [[{'x': 1, 'y': 0, 'z': 0, 'name': NO_RECONSTRUCTION}]])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_type_20_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
            mv.validate([test_marker(x=1, y=0, z=0, name=NO_RECONSTRUCTION)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_type_30_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
            mv.validate([test_marker(x=1, y=0, z=0, name=TYPE_30)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_axon_tips_type_20_valid(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                 test_node(id=2, type=AXON, x=0, y=0, z=0, parent_node_id=1)]
        mv.validate([test_marker(x=0, y=0, z=0, name=AXON)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_coordinate_corresponding_to_dendrite_tips_type_20_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, x=0, y=0, z=0, parent_node_id=1)]
            mv.validate([test_marker(x=1, y=0, z=0, name=AXON)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_number_of_type_30_one(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        mv.validate([test_marker(name=TYPE_30)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_number_of_type_30_less_than_one(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        errors = mv.validate([test_marker(name=NO_RECONSTRUCTION)], test_tree(nodes))
        self.assertMarkerErrors(errors, "Total number of type 30s is 0", [[{}]])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_number_of_type_30_more_than_one(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        errors = mv.validate([test_marker(name=TYPE_30), test_marker(name=TYPE_30)], test_tree(nodes))
        self.assertMarkerErrors(errors, "Total number of type 30s is 2", [[{'x': 0, 'y': 0, 'z': 0, 'name': TYPE_30}],
                                                                          [{'x': 0, 'y': 0, 'z': 0, 'name': TYPE_30}]])

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_number_of_no_reconstruction_one(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        mv.validate([test_marker(name=NO_RECONSTRUCTION)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_number_of_no_reconstruction_zero(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        mv.validate([test_marker(name=CUT_DENDRITE)], test_tree(nodes))

    @patch("neuron_morphology.validation.marker_validators", [mv])
    def test_number_of_no_reconstruction_more_than_one(self):
        nodes = [test_node(id=1, type=SOMA, parent_node_id=-1)]
        errors = mv.validate([test_marker(name=NO_RECONSTRUCTION), test_marker(name=NO_RECONSTRUCTION)],
                             test_tree(nodes))
        self.assertMarkerErrors(errors, "Total number of type 20s is more than one: 2",
                                [[{'x': 0, 'y': 0, 'z': 0, 'name': NO_RECONSTRUCTION}],
                                 [{'x': 0, 'y': 0, 'z': 0, 'name': NO_RECONSTRUCTION}]])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarkerValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
