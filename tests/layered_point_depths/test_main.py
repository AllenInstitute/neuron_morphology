from unittest import TestCase

import xarray as xr
import numpy as np
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString
from scipy.interpolate import RegularGridInterpolator

import neuron_morphology.layered_point_depths.__main__ as lpd

class TestUtilities(TestCase):

    def test_translate_field(self):
        inp = xr.DataArray(
            data=np.eye(10),
            dims=["x", "y"],
            coords = {
                "x": np.arange(10),
                "y": np.arange(10, 20)
            }
        )

        res = lpd.translate_field(inp, 5, 2)

        assert np.allclose(res.coords["x"], np.arange(5, 15))
        assert np.allclose(res.coords["y"], np.arange(12, 22))

    def test_setup_interpolator(self):

        field = xr.DataArray(
            data=np.arange(16).reshape((4, 4)),
            dims=["x", "y"],
            coords = {
                "x": np.arange(4),
                "y": np.arange(4, 8)
            }
        )

        obt = lpd.setup_interpolator(field, dim=None, method="linear")
        self.assertAlmostEqual(
            obt((2.5, 6.5)),
            12.5
        ) 

    def test_containing_layer(self):
        layers = [
            {
                "name": "a",
                "bounds": Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
            },
            {
                "name": "b",
                "bounds":  Polygon([(1, 1), (2, 1), (2, 2), (1, 2), (1, 1)])
            }
        ]

        self.assertEqual(
            lpd.containing_layer((1.5, 1.5), layers),
            "b"
        )

    def test_tuplize(self):
        arr = np.array([1, 2, 3])
        self.assertEqual(
            lpd.tuplize(arr),
            (1, 2, 3)
        )

    def test_step_from_node(self):
        pos = (0, 0)

        depth_interp = RegularGridInterpolator(
            (np.arange(4), np.arange(4)),
            np.arange(16).reshape((4, 4))
        )

        dx_interp = RegularGridInterpolator(
            (np.arange(4), np.arange(4)),
            np.ones((4, 4))
        )
        dy_interp = RegularGridInterpolator(
            (np.arange(4), np.arange(4)),
            np.ones((4, 4)) * 2
        )

        surface = LineString([(0, 2), (4, 2)])

        depth = lpd.step_from_node(
            pos, depth_interp, dx_interp, dy_interp, surface, 1.0, 1000)

        self.assertAlmostEqual(
            depth, 
            depth_interp((1, 2))
        )

    def test_get_node_intersections(self):

        node = {
            "x": 0,
            "y": 0,
            "z": 12,
            "id": 100,
            "type": "foo"
        }

        depth_interp = RegularGridInterpolator(
            (np.arange(4), np.arange(4)),
            np.arange(16).reshape((4, 4))
        )

        dx_interp = RegularGridInterpolator(
            (np.arange(4), np.arange(4)),
            np.ones((4, 4))
        )
        dy_interp = RegularGridInterpolator(
            (np.arange(4), np.arange(4)),
            np.ones((4, 4)) * 2
        )

        layers = [
            {
                "name": "a",
                "bounds": Polygon([(0, 0), (0, 2), (4, 2), (4, 0), (0, 0)]),
                "pia_surface": LineString([(0, 2), (4, 2)]),
                "wm_surface": LineString([(0, 0), (4, 0)])
            }
        ]

        obt = lpd.get_node_intersections(
            node, 
            depth_interp, 
            dx_interp, 
            dy_interp, 
            layers, 
            1.0, 
            1000
        )
        

        self.assertEqual(obt["ids"], node["id"])
        self.assertEqual(obt["point_type"], node["type"])
        self.assertEqual(obt["layer_name"], "a")
        self.assertAlmostEqual(
            obt["local_layer_pia_side_depth"], 
            depth_interp((1, 2))
        )
        self.assertAlmostEqual(
            obt["local_layer_wm_side_depth"], 
            depth_interp((0, 0))
        )

    def test_setup_layers(self):
        bounds = [(0, 0), (0, 2), (4, 2), (4, 0), (0, 0)]
        pia = [[0, 2], [4, 2]]
        wm = [(0, 0), (4, 0)]
        layers = [
            {
                "name": "a",
                "bounds": Polygon(bounds),
                "pia_surface": LineString(pia),
                "wm_surface": LineString(wm)
            }
        ]

        lpd.setup_layers(layers)
        assert np.allclose(
            list(layers[0]["bounds"].exterior.coords),
            bounds
        )