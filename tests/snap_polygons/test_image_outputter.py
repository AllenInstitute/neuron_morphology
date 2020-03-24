import unittest
from unittest import TestCase
from unittest.mock import MagicMock, patch
import tempfile
import shutil
import os
import sys

import pytest
import numpy as np
import imageio
import glymur
import pandas as pd
import matplotlib.pyplot as plt

try:
    import rasterio
    import neuron_morphology.snap_polygons.image_outputter as imgo
    from neuron_morphology.snap_polygons.geometries import Geometries
except ImportError:
    pass

@unittest.skipIf('rasterio' not in sys.modules,
                 'install rasterio to use snap_polygons.geometries')
class TestUtilities(TestCase):

    def test_make_path_patch_open(self):
        vertices = [(0, 0), (1, 0), (1, 1)]
        alpha = 0.1

        obtained = imgo.make_pathpatch(vertices, alpha=alpha)

        obt_path = obtained.get_path()
        obt_verts = obt_path.vertices
        obt_alpha = obtained.get_alpha()

        assert np.allclose(obt_verts, vertices)
        self.assertAlmostEqual(obt_alpha, alpha)

    def test_fname_suffix(self):
        path = "/a/b/c.foo"
        suffix = "baz"

        obt = imgo.fname_suffix(path, suffix)
        self.assertEqual(obt, "/a/b/c_baz.foo")

@unittest.skipIf('rasterio' not in sys.modules,
                 'install rasterio to use snap_polygons.geometries')
class TestImageIo(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_read_png(self):
        path = os.path.join(self.tmpdir, "test.png")
        image = np.arange(16, dtype=np.uint8).reshape(4, 4)
        imageio.imsave(path, image)

        obt = imgo.read_image(path)
        assert np.allclose(obt, image)

    def test_read_png_dec(self):
        path = os.path.join(self.tmpdir, "test_dec.png")
        image = np.arange(16, dtype=np.uint8).reshape(4, 4)
        imageio.imsave(path, image)

        obt = imgo.read_image(path, 2)
        assert np.allclose(
            obt, 
            np.array([
                [0, 2],
                [8, 10]
            ])
        )

    @pytest.mark.skipif( # we are running via pytest
        glymur.version.openjpeg_version < "2.3.0", 
        reason="you must have at openjpeg of at least 2.3.0 to write images"
    )
    def test_read_jp2(self):
        path = os.path.join(self.tmpdir, "test.jp2")
        image = np.random.randint(0, 255, (640, 480), dtype=np.uint8)
        glymur.Jp2k(path, data=image)

        obt = imgo.read_image(path)
        assert np.allclose(obt, image)


    def test_write_figure(self):
        fig, ax = plt.subplots()
        ax.plot(np.arange(2))
        fig2, ax2 = plt.subplots()

        path = os.path.join(self.tmpdir, "test.png")
        path2 = os.path.join(self.tmpdir, "test2.png")

        imgo.write_figure(fig2, path2)
        imgo.write_figure(fig, path)

        self.assertEqual(plt.gcf().number, fig2.number) # current fig is reset
        assert os.stat(path).st_size > os.stat(path2).st_size # correct fig is written

@unittest.skipIf('rasterio' not in sys.modules,
                 'install rasterio to use snap_polygons.geometries')
class TestImageOutputter(TestCase):
    # ImageOutputter has a lot of "does it look right" plotting logic. We 
    # won't be testing that, but we will make sure the overall behavior is OK


    def setUp(self):
        self.native_layer1_path =  [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)]
        self.native = Geometries()
        self.native.register_polygon("layer1", self.native_layer1_path)

        self.result_layer1_path = [(0, 0), (0, 10), (10, 10), (10, 0), (0, 0)]
        self.result_layer1_pia = [(10, 10), (10, 0)]
        self.result = Geometries()
        self.result.register_polygon("layer1", self.result_layer1_path)
        self.result.register_surface("layer1_pia", self.result_layer1_pia)

        self.image_specs = [
            {
                "input_path": "fizz", 
                "output_path": "buzz", 
                "downsample": 8, 
                "overlay_types": ["before", "after"]
            }
        ]

        self.outputter = imgo.ImageOutputter(
            self.native, self.result, self.image_specs)

    def test_draw_before(self):
        fig = self.outputter.draw_before(np.eye(3))
        ax = fig.get_axes()[0]
        vertices = ax.patches[0].get_path().vertices
        assert np.allclose(vertices, self.native_layer1_path)

    def test_draw_after(self):
        fig = self.outputter.draw_after(np.eye(30))
        ax = fig.get_axes()[0]

        poly_vertices = ax.patches[0].get_path().vertices
        assert np.allclose(poly_vertices, self.result_layer1_path)

        surf_vertices = ax.patches[1].get_path().vertices
        assert np.allclose(surf_vertices, self.result_layer1_pia)

    def test_write_images(self):
        with patch(
            "neuron_morphology.snap_polygons.image_outputter.write_figure", 
            new_callable=MagicMock
        ) as write:
            with patch(
                "neuron_morphology.snap_polygons.image_outputter.read_image",
                new=lambda *a, **k: np.eye(30)
            ) as _read:
                obtained = self.outputter.write_images()
                write.assert_called()

        pd.testing.assert_frame_equal(
            pd.DataFrame(obtained), 
            pd.DataFrame({
                "input_path": ["fizz", "fizz"], 
                "downsample": [8, 8],
                "output_path": ["buzz_before", "buzz_after"],
                "overlay_type": ["before", "after"]
            }),
            check_like=True,
            check_dtype=False
        )