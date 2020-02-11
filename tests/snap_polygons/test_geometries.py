from unittest import TestCase

import numpy as np
from shapely.geometry.polygon import Polygon

from neuron_morphology.snap_polygons.geometries import Geometries
import neuron_morphology.snap_polygons.geometries as go
from neuron_morphology.snap_polygons.bounding_box import BoundingBox


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

    def test_transform(self):
        geo = Geometries()
        geo.register_polygons(self.polys)
        geo.register_surfaces(self.surfaces)

        obt = geo.transform(lambda v, h: (v + 2, h + 3))

        assert np.allclose(
            list(obt.surfaces["pia"].coords),
            [(5.0, 6.0), (5.0, 5.0)]
        )

    def test_to_json(self):
        geo = Geometries()
        geo.register_polygons(self.polys)
        geo.register_surfaces(self.surfaces)

        obt = geo.to_json()
        self.assertEqual(len(obt["surfaces"]), 2)
        self.assertEqual(len(obt["polygons"]), 2)

class TestUtilities(TestCase):


    def test_rasterize(self):

        obt = go.rasterize(
            Polygon([(0, 0), (0, 5), (5, 5), (5, 0), (0, 0)]),
            BoundingBox(0, 0, 7, 3)
        )

        assert np.allclose(
            obt, 
            [
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [1, 1, 1],
                [0, 0, 0],
                [0, 0, 0]
            ]
         )

    def test_make_scale(self):
        tx = go.make_scale(5)
        assert np.allclose(
            tx(5, 10),
            [25, 50]
        )

    def test_clear_overlaps(self):

        amask = np.eye(10)
        bmask = np.zeros_like(amask)
        bmask[:5] = 1

        masks = {"a": amask, "b": bmask}
        go.clear_overlaps(masks)

        aexp = np.diagflat([0, 0, 0, 0, 0, 1, 1, 1, 1, 1])
        assert np.allclose(masks["a"], aexp)


    def test_closest_from_stack(self):
        obt_c, obt_n = go.closest_from_stack({
            "a": np.array([0, 1, 2, 3, 4]),
            "b": np.array([4, 3, 2, 1, 0])
        })

        assert np.allclose(obt_c, [1, 1, 1, 2, 2])
        assert obt_n[1] == "a"
        assert obt_n[2] == "b"

    def test_get_snapped_polys(self):
        closest = np.array([
            [1, 1, 1],
            [1, 2, 2],
            [1, 2, 2]
        ])
        names = {1: "a", 2: "b"}

        obt = go.get_snapped_polys(closest, names)
        assert np.allclose(
            list(obt["b"].exterior.coords),
            [(1.0, 1.0), (1.0, 3.0), (3.0, 3.0), (3.0, 1.0), (1.0, 1.0)]
        )

    def find_vertical_surfaces(self):
        polys = {
            "layer1": Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
            "layer2": Polygon([(0, 1), (1, 1), (1, 2), (0, 2), (0, 1)])
        }
        obt = go.find_vertical_surfaces(polys, ["layer1", "layer2"])

        assert np.allclose(
            list(obt["layer2_pia"].coords),
            [(0, 1), (1, 1)]
        )