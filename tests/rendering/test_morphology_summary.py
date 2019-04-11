import unittest
from neuron_morphology.tests import test_node, test_morphology_large, test_morphology_summary, test_tree
from neuron_morphology.constants import *
from PIL import ImageDraw, Image


class TestMorphologySummary(unittest.TestCase):

    def test_set_color_by_node_type(self):

        axon_color = (70, 130, 180)
        basal_dendrite_color = (178, 34, 34)
        apical_dendrite_color = (255, 127, 80)
        color_by_node_type = {AXON: axon_color, BASAL_DENDRITE: basal_dendrite_color,
                              APICAL_DENDRITE: apical_dendrite_color}
        for node_type, expected_color in color_by_node_type.items():
            nodes = [test_node(id=1, type=SOMA, parent_node_id=-1), test_node(id=2, type=node_type, parent_node_id=1)]
            morphology_summary = test_morphology_summary(morphology=test_tree(nodes))
            color = morphology_summary.set_color_by_node_type(nodes)
            self.assertEqual(expected_color, color)

    def test_top(self):

        morphology = test_morphology_large()
        morphology_summary = test_morphology_summary(morphology=morphology, width=100, height=100)
        self.assertEqual(7.493119137224102, morphology_summary.top())

    def test_bottom(self):

        morphology = test_morphology_large()
        morphology_summary = test_morphology_summary(morphology=morphology, width=100, height=100)
        self.assertEqual(92.50688086277589, morphology_summary.bottom())

    def test_transform_swc_to_pia_space(self):

        morphology_summary = test_morphology_summary()
        transformed_morphology = morphology_summary.morphology
        nodes = [test_node(id=1, type=SOMA, x=414.30431375339685, y=-372.1812431503548, z=-1.0799999999999983,
                           radius=34.99999999999999, parent_node_id=-1),
                 test_node(id=2, type=BASAL_DENDRITE, x=806.3898222339458, y=-292.3755162910032, z=-21.079999999999998,
                           radius=2.9999999999999996, parent_node_id=1),
                 test_node(id=3, type=BASAL_DENDRITE, x=806.3898222339458, y=-292.3755162910032, z=-21.079999999999998,
                           radius=2.9999999999999996, parent_node_id=2),
                 test_node(id=4, type=APICAL_DENDRITE, x=557.0026715166243, y=-31.9795695923344, z=-11.079999999999998,
                           radius=2.9999999999999996, parent_node_id=1),
                 test_node(id=5, type=APICAL_DENDRITE, x=557.0026715166243, y=-31.9795695923344, z=-11.079999999999998,
                           radius=2.9999999999999996, parent_node_id=4),
                 test_node(id=6, type=AXON, x=314.0966908760038, y=-379.82534658124416, z=-1.0799999999999983,
                           radius=2.9999999999999996, parent_node_id=1),
                 test_node(id=7, type=AXON, x=314.0966908760038, y=-379.82534658124416, z=-1.0799999999999983,
                           radius=2.9999999999999996, parent_node_id=6)
                 ]
        expected_morphology = test_tree(nodes)
        for node in expected_morphology.nodes():
            self.assertEqual(node['x'], transformed_morphology.node_by_id(node['id'])['x'])
            self.assertEqual(node['y'], transformed_morphology.node_by_id(node['id'])['y'])
            self.assertEqual(node['z'], transformed_morphology.node_by_id(node['id'])['z'])
            self.assertEqual(node['radius'], transformed_morphology.node_by_id(node['id'])['radius'])

    def test_calculate_scale(self):

        morphology_summary = test_morphology_summary(morphology=test_morphology_large(), width=200, height=200)
        scale_factor, scale_inset_x, scale_inset_y = morphology_summary.calculate_scale()
        self.assertEqual((0.32586763962452725, -62.776347988618035, 4.565131415185888), (scale_factor, scale_inset_x,
                                                                                         scale_inset_y))

    def test_draw_morphology_summary_small(self):

        morphology_summary = test_morphology_summary(width=200, height=200)
        expected_img = Image.new("RGBA", (200, 200))
        canvas = ImageDraw.Draw(expected_img)

        canvas.line((40.710550887021455, 167.55275443510732, 0.0, 170.6582633053221),
                    morphology_summary.colors.axon_color)
        canvas.line((40.710550887021455, 167.55275443510732, 200.0, 135.13071895424844),
                    morphology_summary.colors.basal_dendrite_color)
        canvas.line((40.710550887021455, 167.55275443510732, 98.68347338935585, 29.341736694677905),
                    morphology_summary.colors.apical_dendrite_color)
        canvas.ellipse((26, 153, 54, 181),
                       fill=morphology_summary.colors.soma_color,
                       outline=morphology_summary.colors.soma_color)

        result_img = morphology_summary.draw_morphology_summary()
        self.assertEqual(expected_img, result_img)

    def test_draw_morphology_summary_large(self):

        morphology = test_morphology_large()
        morphology_summary = test_morphology_summary(morphology=morphology, width=200, height=200)
        expected_img = Image.new("RGBA", (200, 200))
        canvas = ImageDraw.Draw(expected_img)

        canvas.line((72.23202082046099, 125.84695463311424, 39.57759928102007, 128.33792057518394),
                    morphology_summary.colors.axon_color)
        canvas.line((39.57759928102007, 128.33792057518394, 31.66207942481607, 139.67308880525752),
                    morphology_summary.colors.axon_color)
        canvas.line((31.66207942481607, 139.67308880525752, 23.74655956861207, 151.00825703533104),
                    morphology_summary.colors.axon_color)
        canvas.line((23.74655956861207, 151.00825703533104, 15.831039712408, 162.34342526540468),
                    morphology_summary.colors.axon_color)
        canvas.line((15.831039712408, 162.34342526540468, 7.915519856204, 173.67859349547825),
                    morphology_summary.colors.axon_color)
        canvas.line((7.915519856204, 173.67859349547825, 0.0, 185.01376172555177),
                    morphology_summary.colors.axon_color)

        canvas.line((72.23202082046099, 125.84695463311424, 200.0, 99.8408507929376),
                    morphology_summary.colors.basal_dendrite_color)
        canvas.line((200.0, 99.8408507929376, 192.084480143796, 111.17601902301118),
                    morphology_summary.colors.basal_dendrite_color)
        canvas.line((192.084480143796, 111.17601902301118, 184.16896028759197, 122.51118725308476),
                    morphology_summary.colors.basal_dendrite_color)
        canvas.line((184.16896028759197, 122.51118725308476, 176.25344043138796, 133.8463554831584),
                    morphology_summary.colors.basal_dendrite_color)

        canvas.line((72.23202082046099, 125.84695463311424, 118.73279784306025, 14.98623827444817),
                    morphology_summary.colors.apical_dendrite_color)
        canvas.line((118.73279784306025, 14.98623827444817, 110.81727798685621, 26.321406504521747),
                    morphology_summary.colors.apical_dendrite_color)
        canvas.line((110.81727798685621, 26.321406504521747, 102.90175813065223, 37.656574734595324),
                    morphology_summary.colors.apical_dendrite_color)
        canvas.line((102.90175813065223, 37.656574734595324, 94.98623827444818, 48.9917429646689),
                    morphology_summary.colors.apical_dendrite_color)
        canvas.line((94.98623827444818, 48.9917429646689, 90.2791664326238, 59.75696979909756),
                    morphology_summary.colors.apical_dendrite_color)
        canvas.line((90.2791664326238, 59.75696979909756, 82.36364657641973, 71.09213802917114),
                    morphology_summary.colors.apical_dendrite_color)

        canvas.ellipse((60, 114, 82, 136),
                       fill=morphology_summary.colors.soma_color,
                       outline=morphology_summary.colors.soma_color)

        result_img = morphology_summary.draw_morphology_summary()
        self.assertEqual(expected_img, result_img)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMorphologySummary)
    unittest.TextTestRunner(verbosity=5).run(suite)
