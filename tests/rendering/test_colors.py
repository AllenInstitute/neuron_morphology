import unittest
import allensdk.neuron_morphology.rendering.colors as co
from allensdk.neuron_morphology.constants import *


class TestColors(unittest.TestCase):

    def test_defaults(self):

        color = co.Colors()
        expected_soma_color = (0, 0, 0)
        expected_axon_color = (70, 130, 180)
        expected_basal_dendrite_color = (178, 34, 34)
        expected_apical_dendrite_color = (255, 127, 80)
        expected_layer_boundaries_color = (128, 128, 128, 255)
        expected_img_background_color = (255, 255, 255)
        expected_scale_bar_color = (128, 128, 128, 128)
        self.assertEqual(expected_soma_color, color.DEFAULT_SOMA_COLOR)
        self.assertEqual(expected_axon_color, color.DEFAULT_AXON_COLOR)
        self.assertEqual(expected_basal_dendrite_color, color.DEFAULT_BASAL_DENDRITE_COLOR)
        self.assertEqual(expected_apical_dendrite_color, color.DEFAULT_APICAL_DENDRITE_COLOR)
        self.assertEqual(expected_layer_boundaries_color, color.DEFAULT_LAYER_BOUNDARIES_COLOR)
        self.assertEqual(expected_img_background_color, color.DEFAULT_IMG_BACKGROUND_COLOR)
        self.assertEqual(expected_scale_bar_color, color.DEFAULT_SCALE_BAR_COLOR)

    def test_properties(self):

        color = co.Colors()
        expected_soma_color = (0, 0, 0)
        expected_axon_color = (70, 130, 180)
        expected_basal_dendrite_color = (178, 34, 34)
        expected_apical_dendrite_color = (255, 127, 80)
        expected_layer_boundaries_color = (128, 128, 128, 255)
        expected_img_background_color = (255, 255, 255)
        expected_scale_bar_color = (128, 128, 128, 128)
        self.assertEqual(expected_soma_color, color.soma_color)
        self.assertEqual(expected_axon_color, color.axon_color)
        self.assertEqual(expected_basal_dendrite_color, color.basal_dendrite_color)
        self.assertEqual(expected_apical_dendrite_color, color.apical_dendrite_color)
        self.assertEqual(expected_layer_boundaries_color, color.layer_boundaries_color)
        self.assertEqual(expected_img_background_color, color.img_background_color)
        self.assertEqual(expected_scale_bar_color, color.scale_bar_color)

    def test_get_color_by_node_type_soma(self):

        color = co.Colors()
        expected_soma_color = (0, 0, 0)
        soma_color = color.get_color_by_node_type(SOMA)
        self.assertEqual(expected_soma_color, soma_color)

    def test_get_color_by_node_type_axon(self):

        color = co.Colors()
        expected_axon_color = (70, 130, 180)
        axon_color = color.get_color_by_node_type(AXON)
        self.assertEqual(expected_axon_color, axon_color)

    def test_get_color_by_node_type_basal_dendrite(self):

        color = co.Colors()
        expected_basa_dendrite_color = (178, 34, 34)
        basal_dendrite_color = color.get_color_by_node_type(BASAL_DENDRITE)
        self.assertEqual(expected_basa_dendrite_color, basal_dendrite_color)

    def test_get_color_by_node_type_apical_dendrite(self):

        color = co.Colors()
        expected_apical_dendrite_color = (255, 127, 80)
        apical_color = color.get_color_by_node_type(APICAL_DENDRITE)
        self.assertEqual(expected_apical_dendrite_color, apical_color)

    def test_set_soma_color(self):

        color = co.Colors(soma_color=(100, 100, 100))
        expected_soma_color = (100, 100, 100)
        self.assertEqual(expected_soma_color, color.soma_color)

    def test_set_axon_color(self):
        color = co.Colors(axon_color=(100, 100, 100))
        expected_axon_color = (100, 100, 100)
        self.assertEqual(expected_axon_color, color.axon_color)

    def test_set_basal_dendrite_color(self):
        color = co.Colors(basal_dendrite_color=(100, 100, 100))
        expected_basal_dendrite_color = (100, 100, 100)
        self.assertEqual(expected_basal_dendrite_color, color.basal_dendrite_color)

    def test_set_apical_dendrite_color(self):
        color = co.Colors(apical_dendrite_color=(100, 100, 100))
        expected_apical_dendrite_color = (100, 100, 100)
        self.assertEqual(expected_apical_dendrite_color, color.apical_dendrite_color)

    def test_set_layer_boundaries_color(self):
        color = co.Colors(layer_boundaries_color=(100, 100, 100))
        expected_layer_boundaries_color = (100, 100, 100)
        self.assertEqual(expected_layer_boundaries_color, color.layer_boundaries_color)

    def test_set_img_background_color(self):
        color = co.Colors(img_background_color=(100, 100, 100))
        expected_img_background_color = (100, 100, 100)
        self.assertEqual(expected_img_background_color, color.img_background_color)

    def test_set_scale_bar_color(self):
        color = co.Colors(scale_bar_color=(128, 128, 128, 128))
        expected_scale_bar_color = (128, 128, 128, 128)
        self.assertEqual(expected_scale_bar_color, color.scale_bar_color)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestColors)
    unittest.TextTestRunner(verbosity=5).run(suite)
