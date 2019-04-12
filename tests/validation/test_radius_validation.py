from neuron_morphology.constants import *
from neuron_morphology.validation import radius_validation as rv
from neuron_morphology.validation.result import InvalidMorphology
from tests.objects import test_node, test_tree
from tests.validation.validation_test_case import ValidationTestCase
import unittest
from mock import patch


class TestRadiusValidationFunctions(ValidationTestCase):

    """ Tests the functions in radius_validation.py """

    def test_valid_radius_for_soma(self):
        for valid_radius in [35, 36, 100, 999]:
            nodes = [test_node(type=SOMA, radius=valid_radius)]
            errors = rv.validate_radius_threshold(test_tree(nodes, strict_validation=False))
            self.assertEqual(len(errors), 0)

    def test_invalid_radius_for_soma(self):
        for invalid_radius in [-10, 0, 1, 34, 34.999]:
            nodes = [test_node(type=SOMA, radius=invalid_radius)]
            errors = rv.validate_radius_threshold(test_tree(nodes, strict_validation=False))
            self.assertNodeErrors(errors, "The radius must be", [[1]])

    def test_any_radius_valid_for_axon(self):
        for valid_radius in [-10, 0, 3, float('inf')]:
            nodes = [test_node(id=1, type=SOMA, radius=36, parent_node_id=-1),
                     test_node(id=2, type=AXON, radius=valid_radius, parent_node_id=1)]
            errors = rv.validate_radius_threshold(test_tree(nodes, strict_validation=False))
            self.assertEqual(len(errors), 0)

    def test_valid_radius_for_dendrite(self):
        for valid_radius in [-1, 0, 10, 16, 19.999]:
            for dendrite in [BASAL_DENDRITE, APICAL_DENDRITE]:
                nodes = [test_node(id=1, type=SOMA, radius=36, parent_node_id=-1),
                         test_node(id=2, type=dendrite, radius=valid_radius, parent_node_id=1)]
                errors = rv.validate_radius_threshold(test_tree(nodes, strict_validation=False))
                self.assertEqual(len(errors), 0)

    def test_invalid_radius_for_dendrite(self):
        for valid_radius in [20.002, 35, 40, 100, 1000]:
            for dendrite in [BASAL_DENDRITE, APICAL_DENDRITE]:
                nodes = [test_node(id=1, type=SOMA, radius=36, parent_node_id=-1),
                         test_node(id=2, type=dendrite, radius=valid_radius, parent_node_id=1)]
                errors = rv.validate_radius_threshold(test_tree(nodes, strict_validation=False))
                self.assertNodeErrors(errors, "The radius must be", [[2]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_valid_radius_multiple_types(self):
        nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                 test_node(id=2, type=AXON, radius=2.0, parent_node_id=-1),
                 test_node(id=3, type=BASAL_DENDRITE, radius=3.0, parent_node_id=1),
                 test_node(id=4, type=BASAL_DENDRITE, radius=2.0, parent_node_id=3),
                 test_node(id=5, type=APICAL_DENDRITE, radius=3.0, parent_node_id=1),
                 test_node(id=6, type=APICAL_DENDRITE, radius=2.0, parent_node_id=5)]
        test_tree(nodes)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_invalid_radius_multiple_types(self):
        try:
            nodes = [test_node(id=1, type=SOMA, radius=2.0, parent_node_id=-1),
                     test_node(id=2, type=AXON, radius=2.0, parent_node_id=-1),
                     test_node(id=3, type=BASAL_DENDRITE, radius=32.0, parent_node_id=1),
                     test_node(id=4, type=APICAL_DENDRITE, radius=32.0, parent_node_id=1)]
            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "The radius must be", [[1], [3], [4]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_absence_of_constriction_for_dendrite(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=12.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=11.0, parent_node_id=2),
                     test_node(id=4, type=dendrite_type, radius=10.0, parent_node_id=3)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_absence_of_constriction_for_dendrite_one_child_less_than_limit(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=10.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=5.0, parent_node_id=2),
                     test_node(id=4, type=dendrite_type, radius=6.0, parent_node_id=3)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_absence_of_constriction_for_dendrite_multiple_children_less_than_limit(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=12.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=11.0, parent_node_id=2),
                     test_node(id=4, type=dendrite_type, radius=10.0, parent_node_id=2)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_existence_of_constriction_for_dendrite_one_child_less_than_limit(self):
        try:
            for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
                nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                         test_node(id=2, type=dendrite_type, radius=1.0, parent_node_id=1)]

                test_tree(nodes, strict_validation=True)

            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Constriction: The radius of types 3 and 4 should not be less "
                                                       "than 2.0px", [[2]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_existence_of_constriction_for_dendrite_multiple_children(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            try:
                nodes = [test_node(id=1, type=SOMA, radius=35.1, parent_node_id=-1),
                         test_node(id=2, type=dendrite_type, radius=2.0, parent_node_id=1),
                         test_node(id=3, type=dendrite_type, radius=2.0, parent_node_id=2),
                         test_node(id=4, type=dendrite_type, radius=1.5, parent_node_id=3),
                         test_node(id=5, type=dendrite_type, radius=1.5, parent_node_id=3)]

                test_tree(nodes, strict_validation=True)

                self.fail("Morphology should have been rejected.")
            except InvalidMorphology as e:
                self.assertNodeErrors(e.validation_errors, "Constriction: The radius of types 3 and 4 should not be "
                                                           "less than 2.0px", [[5], [4]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_absence_of_constriction_for_dendrite_after_node_ten_from_soma(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=10.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=11.0, parent_node_id=2),
                     test_node(id=4, type=dendrite_type, radius=12.0, parent_node_id=3),
                     test_node(id=5, type=dendrite_type, radius=12.0, parent_node_id=4),
                     test_node(id=6, type=dendrite_type, radius=12.0, parent_node_id=5),
                     test_node(id=7, type=dendrite_type, radius=12.0, parent_node_id=6),
                     test_node(id=8, type=dendrite_type, radius=12.0, parent_node_id=7),
                     test_node(id=9, type=dendrite_type, radius=12.0, parent_node_id=8),
                     test_node(id=10, type=dendrite_type, radius=12.0, parent_node_id=9),
                     test_node(id=11, type=dendrite_type, radius=12.0, parent_node_id=10),
                     test_node(id=12, type=dendrite_type, radius=1.5, parent_node_id=11)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_extreme_taper_less_than_eight_nodes_in_segment(self):
        nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                 test_node(id=2, type=BASAL_DENDRITE, radius=2.0, parent_node_id=1),
                 test_node(id=3, type=BASAL_DENDRITE, radius=2.0, parent_node_id=2),
                 test_node(id=4, type=BASAL_DENDRITE, radius=2.0, parent_node_id=3)]

        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_absence_of_extreme_taper_for_dendrite_more_than_eight_nodes_in_one_segment(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=4.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=4.0, parent_node_id=2),
                     test_node(id=4, type=dendrite_type, radius=4.0, parent_node_id=3),
                     test_node(id=5, type=dendrite_type, radius=4.0, parent_node_id=4),
                     test_node(id=6, type=dendrite_type, radius=4.0, parent_node_id=5),
                     test_node(id=7, type=dendrite_type, radius=4.0, parent_node_id=6),
                     test_node(id=8, type=dendrite_type, radius=3.0, parent_node_id=7),
                     test_node(id=9, type=dendrite_type, radius=3.0, parent_node_id=8)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_existence_of_extreme_taper_for_dendrite_more_than_eight_nodes_in_one_segment(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            try:
                nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                         test_node(id=2, type=dendrite_type, radius=12.0, parent_node_id=1),
                         test_node(id=3, type=dendrite_type, radius=12.0, parent_node_id=2),
                         test_node(id=4, type=dendrite_type, radius=12.0, parent_node_id=3),
                         test_node(id=5, type=dendrite_type, radius=12.0, parent_node_id=4),
                         test_node(id=6, type=dendrite_type, radius=12.0, parent_node_id=5),
                         test_node(id=7, type=dendrite_type, radius=12.0, parent_node_id=6),
                         test_node(id=8, type=dendrite_type, radius=2.0, parent_node_id=7),
                         test_node(id=9, type=dendrite_type, radius=2.0, parent_node_id=8)]

                test_tree(nodes, strict_validation=True)
                self.fail("Morphology should have been rejected.")
            except InvalidMorphology as e:
                self.assertNodeErrors(e.validation_errors, "Extreme Taper: For types 3 and 4", [[2, 8]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_absence_of_extreme_taper_for_dendrite_more_than_eight_nodes_multiple_segments(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=4.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=4.0, parent_node_id=2),
                     test_node(id=4, type=dendrite_type, radius=4.0, parent_node_id=3),
                     test_node(id=5, type=dendrite_type, radius=4.0, parent_node_id=4),
                     test_node(id=6, type=dendrite_type, radius=4.0, parent_node_id=5),
                     test_node(id=7, type=dendrite_type, radius=4.0, parent_node_id=6),
                     test_node(id=8, type=dendrite_type, radius=3.0, parent_node_id=7),
                     test_node(id=9, type=dendrite_type, radius=3.0, parent_node_id=8),
                     test_node(id=10, type=dendrite_type, radius=4.0, parent_node_id=1),
                     test_node(id=11, type=dendrite_type, radius=4.0, parent_node_id=10),
                     test_node(id=12, type=dendrite_type, radius=4.0, parent_node_id=11),
                     test_node(id=13, type=dendrite_type, radius=4.0, parent_node_id=12),
                     test_node(id=14, type=dendrite_type, radius=4.0, parent_node_id=13),
                     test_node(id=15, type=dendrite_type, radius=4.0, parent_node_id=14),
                     test_node(id=16, type=dendrite_type, radius=2.0, parent_node_id=15),
                     test_node(id=17, type=dendrite_type, radius=2.0, parent_node_id=16)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_existence_of_extreme_taper_for_dendrite_more_than_eight_nodes_multiple_segments(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            try:
                nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                         test_node(id=2, type=dendrite_type, radius=10.0, parent_node_id=1),
                         test_node(id=3, type=dendrite_type, radius=10.0, parent_node_id=2),
                         test_node(id=4, type=dendrite_type, radius=10.0, parent_node_id=3),
                         test_node(id=5, type=dendrite_type, radius=10.0, parent_node_id=4),
                         test_node(id=6, type=dendrite_type, radius=10.0, parent_node_id=5),
                         test_node(id=7, type=dendrite_type, radius=10.0, parent_node_id=6),
                         test_node(id=8, type=dendrite_type, radius=2.0, parent_node_id=7),
                         test_node(id=9, type=dendrite_type, radius=2.0, parent_node_id=8),
                         test_node(id=10, type=dendrite_type, radius=10.0, parent_node_id=1),
                         test_node(id=11, type=dendrite_type, radius=10.0, parent_node_id=10),
                         test_node(id=12, type=dendrite_type, radius=10.0, parent_node_id=11),
                         test_node(id=13, type=dendrite_type, radius=10.0, parent_node_id=12),
                         test_node(id=14, type=dendrite_type, radius=10.0, parent_node_id=13),
                         test_node(id=15, type=dendrite_type, radius=10.0, parent_node_id=14),
                         test_node(id=16, type=dendrite_type, radius=2.0, parent_node_id=15),
                         test_node(id=17, type=dendrite_type, radius=2.0, parent_node_id=16)]

                test_tree(nodes, strict_validation=True)
                self.fail("Morphology should have been rejected.")
            except InvalidMorphology as e:
                self.assertNodeErrors(e.validation_errors, "Extreme Taper: For types 3 and 4", [[2, 8], [10, 16]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_decreasing_radius_when_going_away_from_soma_dendrite_valid(self):
        nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                 test_node(id=2, type=BASAL_DENDRITE, radius=4.0, parent_node_id=1),
                 test_node(id=3, type=BASAL_DENDRITE, radius=2.0, parent_node_id=2),
                 test_node(id=4, type=APICAL_DENDRITE, radius=4.0, parent_node_id=1),
                 test_node(id=5, type=APICAL_DENDRITE, radius=2.0, parent_node_id=4)]

        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_decreasing_radius_when_going_away_from_soma_dendrite_one_branch_valid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=dendrite_type, radius=2.0, parent_node_id=1),
                     test_node(id=3, type=dendrite_type, radius=4.0, parent_node_id=2)]

            test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_decreasing_radius_when_going_away_from_soma_dendrite_multiple_branches_invalid(self):
        for dendrite_type in [BASAL_DENDRITE, APICAL_DENDRITE]:
            try:

                nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                         test_node(id=2, type=dendrite_type, radius=2.0, parent_node_id=1),
                         test_node(id=3, type=dendrite_type, radius=2.0, parent_node_id=2),
                         test_node(id=4, type=dendrite_type, radius=4.0, parent_node_id=2),
                         test_node(id=5, type=dendrite_type, radius=2.0, parent_node_id=1),
                         test_node(id=6, type=dendrite_type, radius=2.0, parent_node_id=4)]

                test_tree(nodes, strict_validation=True)
                self.fail("Morphology should have been rejected.")
            except InvalidMorphology as e:
                self.assertNodeErrors(e.validation_errors, "Radius should have a negative slope for the following type: %s"
                                      % dendrite_type, [[]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_decreasing_radius_when_going_away_from_soma_axon_valid(self):
        nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                 test_node(id=2, type=AXON, radius=4.0, parent_node_id=1),
                 test_node(id=3, type=AXON, radius=4.0, parent_node_id=2),
                 test_node(id=4, type=AXON, radius=4.0, parent_node_id=1),
                 test_node(id=5, type=AXON, radius=4.0, parent_node_id=4)]

        test_tree(nodes, strict_validation=True)

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_decreasing_radius_when_going_away_from_soma_basal_dendrite_invalid(self):
        try:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=BASAL_DENDRITE, radius=2.0, parent_node_id=1),
                     test_node(id=3, type=BASAL_DENDRITE, radius=2.0, parent_node_id=2),
                     test_node(id=4, type=BASAL_DENDRITE, radius=2.0, parent_node_id=3),
                     test_node(id=5, type=BASAL_DENDRITE, radius=2.0, parent_node_id=4),
                     test_node(id=6, type=BASAL_DENDRITE, radius=2.0, parent_node_id=5),
                     test_node(id=7, type=BASAL_DENDRITE, radius=2.0, parent_node_id=6),
                     test_node(id=8, type=BASAL_DENDRITE, radius=2.0, parent_node_id=7),
                     test_node(id=9, type=BASAL_DENDRITE, radius=2.0, parent_node_id=7),
                     test_node(id=10, type=BASAL_DENDRITE, radius=19.0, parent_node_id=8),
                     test_node(id=11, type=BASAL_DENDRITE, radius=19.0, parent_node_id=9),
                     test_node(id=12, type=BASAL_DENDRITE, radius=19.0, parent_node_id=10),
                     test_node(id=13, type=BASAL_DENDRITE, radius=19.0, parent_node_id=11),
                     test_node(id=14, type=BASAL_DENDRITE, radius=19.0, parent_node_id=12)]

            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Radius should have a negative slope for the following type: %s"
                                  % BASAL_DENDRITE, [[]])

    @patch("neuron_morphology.validation.swc_validators", [rv])
    def test_decreasing_radius_when_going_away_from_soma_apical_dendrite_invalid(self):
        try:
            nodes = [test_node(id=1, type=SOMA, radius=36.0, parent_node_id=-1),
                     test_node(id=2, type=APICAL_DENDRITE, radius=2.0, parent_node_id=1),
                     test_node(id=3, type=APICAL_DENDRITE, radius=2.0, parent_node_id=2),
                     test_node(id=4, type=APICAL_DENDRITE, radius=2.0, parent_node_id=3),
                     test_node(id=5, type=APICAL_DENDRITE, radius=2.0, parent_node_id=4),
                     test_node(id=6, type=APICAL_DENDRITE, radius=2.0, parent_node_id=5),
                     test_node(id=7, type=APICAL_DENDRITE, radius=2.0, parent_node_id=6),
                     test_node(id=8, type=APICAL_DENDRITE, radius=2.0, parent_node_id=7),
                     test_node(id=9, type=APICAL_DENDRITE, radius=2.0, parent_node_id=7),
                     test_node(id=10, type=APICAL_DENDRITE, radius=19.0, parent_node_id=8),
                     test_node(id=11, type=APICAL_DENDRITE, radius=19.0, parent_node_id=9),
                     test_node(id=12, type=APICAL_DENDRITE, radius=19.0, parent_node_id=10),
                     test_node(id=13, type=APICAL_DENDRITE, radius=19.0, parent_node_id=11),
                     test_node(id=14, type=APICAL_DENDRITE, radius=19.0, parent_node_id=12)]

            test_tree(nodes, strict_validation=True)
            self.fail("Morphology should have been rejected.")
        except InvalidMorphology as e:
            self.assertNodeErrors(e.validation_errors, "Radius should have a negative slope for the following type: %s"
                                  % APICAL_DENDRITE, [[]])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestRadiusValidationFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
