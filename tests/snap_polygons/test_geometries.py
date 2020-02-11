from unittest import TestCase

import numpy as np

from neuron_morphology.snap_polygons.geometries import Geometries


class TestGeometries(TestCase):

    def setUp(self):
        self.polys = {
            "layer1": [(0, 0), (0, 1), (1, 1), (1, 0), (0, 0)],
            "layer2": [(1, 1), (1, 2), (2, 2), (2, 1), (1, 1)],
        }
        self.surfaces = {
            "pia": [(3, 3), (3, 2)],
            "wm": [(0, 0), (0, 1)]
        }

    def test_register_polygons(self):
        geo = Geometries()
        geo.register_polygons(self.polys)
        assert np.allclose([0, 0, 2, 2], geo.close_bounds.coordinates)

    def test_register_surfaces(self):
        geo = Geometries()
        geo.register_surfaces(self.surfaces)
        assert np.allclose([0, 0, 3, 3], geo.close_bounds.coordinates)

    def test_rasterize(self):
        geo = Geometries()
        geo.register_polygons(self.polys)

        obt = geo.rasterize()

        assert np.allclose(
            obt["layer1"],
            [[1, 0], [0, 0]]
        )
        assert np.allclose(
            obt["layer2"],
            [[0, 0], [0, 1]]
        )
