import unittest
from neuron_morphology.validation import validate_reconstruction


class TestValidateReconstructionFunctions(unittest.TestCase):
    """ Tests the functions in validate_reconstruction.py """

    def test_parser_with_one_swc(self):
        parser = validate_reconstruction.parse_arguments(['--swc', 'tests.swc'])
        self.assertTrue(parser.swc, ["tests.swc"])

    def test_parser_with_one_marker(self):
        parser = validate_reconstruction.parse_arguments(['--marker', 'tests.marker'])
        self.assertTrue(parser.marker, ["tests.marker"])

    def test_parser_without_argument(self):
        parser = validate_reconstruction.parse_arguments([])
        self.assertEqual(parser.dir, None)
        self.assertEqual(parser.swc, None)
        self.assertEqual(parser.swc, None)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidateReconstructionFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)