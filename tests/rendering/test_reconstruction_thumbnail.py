import os
import unittest
import allensdk.neuron_morphology.rendering.reconstruction_thumbnail as rt
from tests.test_objects import test_pia_transform, test_soma_depth, test_relative_soma_depth
from PIL import Image, ImageChops


class TestReconstructionThumbnail(unittest.TestCase):

    data_dir = os.path.join(os.path.dirname(__file__), os.pardir, 'data')
    swc_file = os.path.join(data_dir, 'test_swc.swc')

    def test_morphology_summary_thumbnail_cortex(self):

        thumbnail_width = 100
        thumbnail_height = 100
        cortex_thumbnail_file = os.path.join(self.data_dir, 'cortex_morphology_summary.png')

        result_img = rt.morphology_summary_thumbnail(self.swc_file, thumbnail_width, thumbnail_height, [1, 2, 3, 4],
                                                     test_pia_transform)

        test_img = Image.open(cortex_thumbnail_file)
        self.equal_images(result_img, test_img)

    def test_morphology_summary_density_graph_thumbnail(self):

        thumbnail_width = 100
        thumbnail_height = 100
        morphology_summary_thumbnail_file = os.path.join(self.data_dir, 'morphology_summary.png')

        result_img = rt.morphology_summary_density_graph_thumbnail(self.swc_file, test_soma_depth,
                                                                   test_relative_soma_depth, thumbnail_width,
                                                                   thumbnail_height, [1, 2, 3, 4], test_pia_transform,
                                                                   scale_bar=True)

        test_img = Image.open(morphology_summary_thumbnail_file)
        self.equal_images(result_img, test_img)

    def test_morphology_summary_density_graph_high_resolution_thumbnail(self):

        thumbnail_width = 400
        thumbnail_height = 400
        high_res_morphology_summary_thumbnail_file = os.path.join(self.data_dir, 'high_res_morphology_summary.png')

        result_img = rt.morphology_summary_density_graph_thumbnail(self.swc_file, test_soma_depth,
                                                                   test_relative_soma_depth, thumbnail_width,
                                                                   thumbnail_height, [1, 2, 3, 4], test_pia_transform,
                                                                   scale_bar=True)

        test_img = Image.open(high_res_morphology_summary_thumbnail_file)
        self.equal_images(result_img, test_img)

    def test_morphology_summary_density_graph_normalized_depth_thumbnail(self):

        thumbnail_width = 400
        thumbnail_height = 400
        normalized_depth_morphology_summary_thumbnail_file = os.path.join(self.data_dir,
                                                                          'normalized_depth_morphology_summary.png')

        result_img = rt.morphology_summary_density_graph_thumbnail(self.swc_file, test_soma_depth,
                                                                   test_relative_soma_depth, thumbnail_width,
                                                                   thumbnail_height, [1, 2, 3, 4], test_pia_transform
                                                                   , normalized_depth=True)

        test_img = Image.open(normalized_depth_morphology_summary_thumbnail_file)
        self.equal_images(result_img, test_img)

    def equal_images(self, image1, image2):
        return ImageChops.difference(image1, image2).getbbox() is None


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReconstructionThumbnail)
    unittest.TextTestRunner(verbosity=5).run(suite)
