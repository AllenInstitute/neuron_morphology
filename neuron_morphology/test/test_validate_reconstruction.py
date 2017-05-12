import unittest
import sys
from neuron_morphology import validate_reconstruction


class TestValidateReconstructionFunctions(unittest.TestCase):
    """ Tests the functions in validate_reconstruction.py """

    def test_parser_with_one_swc(self):
        parser = validate_reconstruction.parse_arguments(['--swc', 'test.swc'])
        self.assertTrue(parser.swc, ["test.swc"])

    def test_parser_with_one_marker(self):
        parser = validate_reconstruction.parse_arguments(['--marker', 'test.marker'])
        self.assertTrue(parser.marker, ["test.marker"])

    def test_parser_without_argument(self):
        parser = validate_reconstruction.parse_arguments([])
        self.assertEqual(parser.dir, None)
        self.assertEqual(parser.swc, None)
        self.assertEqual(parser.swc, None)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidateReconstructionFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
