import unittest
import allensdk.neuron_morphology.rendering.reconstruction_tile_viewer as rtv
import os
import codecs
import difflib


class TestReconstructionTileViewer(unittest.TestCase):

    data_dir = os.path.join(os.path.dirname(__file__), os.pardir, 'data')

    def test_parse_csv(self):

        input_csv_file = os.path.join(os.path.dirname(__file__), os.pardir, 'data',
                                      'reconstruction_tile_viewer_input.csv')
        expected_dictionary = [{'column1': 'data11', 'column2': 'data12', 'column3': 'data13'},
                               {'column1': 'data21', 'column2': 'data22', 'column3': 'data23'},
                               {'column1': 'data31', 'column2': 'data32', 'column3': 'data33'}]

        self.assertEqual(rtv.parse_csv(input_csv_file), expected_dictionary)

    def test_is_thumbnail_key_true(self):

        data_key = 'test_thumbnail'
        is_thumbnail = rtv.is_thumbnail(data_key, '')
        self.assertTrue(is_thumbnail)

    def test_is_thumbnail_key_false(self):

        data_key = 'test'
        is_thumbnail = rtv.is_thumbnail(data_key, '')
        self.assertFalse(is_thumbnail)

    def test_is_thumbnail_value_true(self):

        data_thumbnail = os.path.join(self.data_dir, 'morphology_summary.png')
        is_thumbnail = rtv.is_thumbnail('', data_thumbnail)
        self.assertTrue(is_thumbnail)

    def test_is_thumbnail_value_false(self):

        data_thumbnail = os.path.join(self.data_dir, 'test_swc.swc')
        is_thumbnail = rtv.is_thumbnail('', data_thumbnail)
        self.assertFalse(is_thumbnail)

    def test_create_tile_viewer(self):

        input_csv_file = os.path.join(self.data_dir, 'reconstruction_tile_viewer_input_data.csv')

        reconstruction_hierarchy = [{'attribute': 'layer', 'sort': 'asc'}, {'attribute': 'structure', 'sort': 'asc'}]
        reconstruction_card_properties = [{'attribute': 'normalized_depth', 'sort': 'asc'},
                                          {'attribute': 'max_euclidean_distance', 'sort': 'asc'},
                                          {'attribute': 'cell_id', 'sort': 'asc'},
                                          {'attribute': 'high_res_thumbnails', 'sort': 'asc'},
                                          {'attribute': '20x_link', 'sort': 'asc'}]
        max_columns = '3'

        morphology_viewer_test_file = os.path.join(self.data_dir, 'test_html.html')
        expected_html = codecs.open(morphology_viewer_test_file, encoding='utf-8').read()

        test_html = rtv.create_tile_viewer(input_csv_file, reconstruction_hierarchy, reconstruction_card_properties,
                                           max_columns)

        self.assertEqual(expected_html, test_html)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReconstructionTileViewer)
    unittest.TextTestRunner(verbosity=5).run(suite)
