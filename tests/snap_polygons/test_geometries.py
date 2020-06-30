import unittest
from unittest import TestCase
import sys
from functools import partial

import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point, LineString

try:
    import rasterio
    from neuron_morphology.snap_polygons.geometries import Geometries
    import neuron_morphology.snap_polygons.geometries as go
except ImportError:
    pass


from neuron_morphology.snap_polygons.bounding_box import BoundingBox


requires_rasterio = unittest.skipIf(
    'rasterio' not in sys.modules,
    'install rasterio to use snap_polygons.geometries'
)


@requires_rasterio
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


@requires_rasterio
class TestGeometriesSnap(TestCase):

    def setUp(self):
        polys = {
            "layer1": [(0, 0), (5, 3), (0, 3)],
            "layer2": [(0, 0), (5, 0), (5, -2), (0, -2)]
        }
        surfs = {
            "pia": [(-2, 4), (7, 4)],
            "wm": [(-2, -2), (7, -2)]
        }

        self.geo = go.Geometries()
        self.geo.register_polygons(polys)
        self.geo.register_surfaces(surfs)

    def test_fill_gaps(self):
        obtained = self.geo.fill_gaps(128.0)

        expected = {
            "layer1": 29.5725,
            "layer2": 24.4227
        }
        for key, area_expt in expected.items():
            with self.subTest():
                area_obt = obtained.polygons[key].area
                self.assertAlmostEqual(area_obt, area_expt, 1)

    def test_cut(self):
        template = Polygon([(-2, 4), (4, 4), (4, -2), (-2, -2)])
        obtained = self.geo.cut(template)
        
        expected = {
            "layer1": Polygon([(4, 2.4), (0, 0), (0, 3), (4, 3)]),
            "layer2": Polygon([(0, -2), (4, -2), (4, 0), (0, 0)][::-1])
        }

        for key, expt in expected.items():
            with self.subTest():
                obt = obtained.polygons[key]
                print(key, obt, expt)
                self.assertEqual(obt, expt)

    def test_convex_hull(self):
        self.assertEqual(self.geo.convex_hull(surfaces=False).area, 25)


@requires_rasterio
class TestUtilities(TestCase):


    def test_rasterize(self):

        obt = go.rasterize(
            Polygon([(0, 0), (0, 5), (5, 5), (5, 0), (0, 0)]),
            BoundingBox(0, 0, 3, 7)
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

    def test_make_translation(self):
        tx = go.make_translation(10, 4)
        assert np.allclose(
            tx(5, 10),
            [15, 14]
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

        resolver = partial(go.select_largest_subpolygon, error_threshold=0)
        obt = go.get_snapped_polys(closest, names, resolver)
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

    def test_select_largest_subpolygon(self):
        cases = [
            # no geometries with nonzero error
            [[Point(0, 1)], None, None, ValueError],
            # only one geometry
            [[Polygon([(0, 0), (1, 0), (1, 1)])], None, Polygon([(0, 0), (1, 0), (1, 1)]), None],
            # a polygon argued directly
            [Polygon([(0, 0), (1, 0), (1, 1)]), None, Polygon([(0, 0), (1, 0), (1, 1)]), None],
            # two polygons of different areas
            [[
                Polygon([(0, 0), (1, 0), (1, 1)]),
                Polygon([(0, 0), (0.5, 0), (0.5, 0.5)]),
            ], 0.0, Polygon([(0, 0), (1, 0), (1, 1)]), None],
            # two polygons whose areas are within the threshold of one another
            [[
                Polygon([(0, 0), (1, 0), (1, 1)]),
                Polygon([(0, 0), (0.5, 0), (0.5, 0.5)]),
            ], 5.0, Polygon([(0, 0), (1, 0), (1, 1)]), ValueError]
        ]

        for polys, threshold, expected, error in cases:
            with self.subTest():
                if error is not None:
                    with self.assertRaises(error):
                        go.select_largest_subpolygon(polys, threshold)
                else:
                    obtained = go.select_largest_subpolygon(polys, threshold)
                    self.assertEqual(obtained, expected)

    def test_shared_faces(self):
        cases = [
            [
                Polygon([(0, 0), (0, 1), (1, 1), (2, 1), (2, 0)]),
                [
                    Polygon([(0, 1), (0, 2), (1, 2), (1, 1)]),
                    Polygon([(1, 1), (1, 2), (2, 2), (2, 1)])
                ],
                LineString([(0, 1), (1, 1), (2, 1)])
            ]
        ]

        for poly, others, expected in cases:
            with self.subTest():
                obtained = go.shared_faces(poly, others)
                print(obtained, expected)
                self.assertEqual(obtained, expected)