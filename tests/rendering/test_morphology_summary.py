import unittest
from tests.test_objects import test_node, test_morphology_small, test_morphology_large, test_morphology_summary
from allensdk.neuron_morphology import compartment
from allensdk.neuron_morphology.constants import *
import allensdk.neuron_morphology.morphology as m
from PIL import ImageDraw, Image


class TestMorphologySummary(unittest.TestCase):

    def test_set_color_by_node_type(self):

        axon_color = (70, 130, 180)
        basal_dendrite_color = (178, 34, 34)
        apical_dendrite_color = (255, 127, 80)
        color_by_node_type = {AXON: axon_color, BASAL_DENDRITE: basal_dendrite_color,
                              APICAL_DENDRITE: apical_dendrite_color}
        for node_type, expected_color in color_by_node_type.items():
            node1 = test_node(id=1, type=SOMA, parent_node_id=-1)
            node2 = test_node(id=2, type=node_type, parent_node_id=1)
            test_segment = compartment.Compartment(node1, node2)
            morphology = m.Morphology([node1, node2], strict_validation=False)
            morphology_summary = test_morphology_summary(morphology=morphology)
            color = morphology_summary.set_color_by_node_type(test_segment)
            self.assertEqual(expected_color, color)

    def test_top(self):

        morphology = test_morphology_large()
        morphology_summary = test_morphology_summary(morphology=morphology, width=100, height=100)
        self.assertEqual(7.493119137224085, morphology_summary.top())

    def test_bottom(self):

        morphology = test_morphology_large()
        morphology_summary = test_morphology_summary(morphology=morphology, width=100, height=100)
        self.assertEqual(92.50688086277589, morphology_summary.bottom())

    def test_transform_swc_to_pia_space(self):

        morphology = test_morphology_small()
        morphology_summary = test_morphology_summary()
        transformed_morphology = morphology_summary._transform_swc_to_pia_space(morphology)
        expected_morphology = m.Morphology([test_node(id=1, type=SOMA, x=414.30431375339685, y=-445.63910059415724,
                                                      z=-1.0799999999999983, radius=34.27116402313359,
                                                      parent_node_id=-1),
                                            test_node(id=2, type=BASAL_DENDRITE, x=806.3898222339457,
                                                      y=-292.3755162910032, z=-21.079999999999998,
                                                      radius=2.9375283448400222, parent_node_id=1),
                                            test_node(id=6, type=APICAL_DENDRITE, x=557.0026715166243,
                                                      y=-31.97956959233437, z=-11.079999999999998,
                                                      radius=2.9375283448400222, parent_node_id=1),
                                            test_node(id=12, type=AXON, x=314.09669087600366, y=-379.8253465812442,
                                                      z=-1.0799999999999983,
                                                      radius=2.9375283448400222, parent_node_id=1)])
        for node in expected_morphology.node_list:
            self.assertEqual(node.x, transformed_morphology.node(node.n).x)

    def test_calculate_scale(self):

        morphology_summary = test_morphology_summary(morphology=test_morphology_large(), width=200, height=200)
        scale_factor, scale_inset_x, scale_inset_y = morphology_summary.calculate_scale()
        self.assertEqual((0.3258676396245273, -62.77634798861804, 4.56513141518586), (scale_factor, scale_inset_x,
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
        canvas.ellipse((26, 153, 53, 180),
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

        canvas.ellipse((61, 114, 83, 136),
                       fill=morphology_summary.colors.soma_color,
                       outline=morphology_summary.colors.soma_color)

        result_img = morphology_summary.draw_morphology_summary()
        self.assertEqual(expected_img, result_img)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMorphologySummary)
    unittest.TextTestRunner(verbosity=5).run(suite)
