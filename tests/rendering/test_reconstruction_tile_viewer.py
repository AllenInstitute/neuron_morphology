import unittest
import allensdk.neuron_morphology.rendering.reconstruction_tile_viewer as rtv
import os


class TestReconstructionTileViewer(unittest.TestCase):

    def test_parse_csv(self):

        input_csv_file = os.path.join(os.path.dirname(__file__), os.pardir, 'data',
                                      'reconstruction_tile_viewer_input.csv')
        expected_dictionary = [{'column1': 'data11', 'column2': 'data12', 'column3': 'data13'},
                               {'column1': 'data21', 'column2': 'data22', 'column3': 'data23'},
                               {'column1': 'data31', 'column2': 'data32', 'column3': 'data33'}]

        self.assertEqual(rtv.parse_csv(input_csv_file), expected_dictionary)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReconstructionTileViewer)
    unittest.TextTestRunner(verbosity=5).run(suite)
