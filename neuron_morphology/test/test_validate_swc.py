import unittest
from neuron_morphology import validate_swc


class TestValidateSWCFunctions(unittest.TestCase):
    """ Tests the functions in validate_swc.py """

    def test_parser_with_one_argument(self):
        parser = validate_swc.parse_arguments(['test.swc'])
        self.assertTrue(parser.file_names, ["test.swc"])

    def test_parser_with_multiple_argument(self):
        parser = validate_swc.parse_arguments(['test1.swc', 'test2.swc'])
        self.assertTrue(parser.file_names, ["test1.swc", "test1.swc"])

    def test_parser_without_argument(self):
        with self.assertRaises(SystemExit) as cm:
            validate_swc.parse_arguments([])
            self.assertEqual(2, cm.exception.code)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestValidateSWCFunctions)
    unittest.TextTestRunner(verbosity=5).run(suite)
