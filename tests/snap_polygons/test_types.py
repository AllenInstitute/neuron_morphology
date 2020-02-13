from unittest import TestCase

from shapely.geometry.polygon import Polygon
import numpy as np

import neuron_morphology.snap_polygons.types as typ


class TestTypeUtils(TestCase):

    def test_ensure_polygon(self):
        obt = typ.ensure_polygon("0,0,1,0,1,1,0,1,0,0")
        assert np.allclose(
            list(obt.exterior.coords),
            [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        )

    def test_ensure_linestring(self):
        obt = typ.ensure_linestring("0,0,1,0,1,1,0,1")
        assert np.allclose(
            list(obt.coords),
            [(0, 0), (1, 0), (1, 1), (0, 1)]
        )

    def test_ensure_path(self):
        obt = typ.ensure_path([(0, 0), (1, 0), (1, 1), (0, 1)])
        obt2 = typ.ensure_path("0,0,1,0,1,1,0,1")
        assert np.allclose(
            obt,
            obt2
        )

    def test_split_pathstring(self):
        obt = typ.split_pathstring("0,0,1,0,1,1,0,1")
        assert np.allclose(
            obt,
            [(0, 0), (1, 0), (1, 1), (0, 1)]
        )