import unittest

import numpy as np

from neuron_morphology.transforms import streamline as sl


class TestCCW(unittest.TestCase):

    def test_ccw_correct(self):
        """
            line1 (0, 1) <- (1, 1)
            line2 (0, 0) -> (1, 0)
        """
        line1 = [(1, 1), (0, 1)]
        line2 = [(0, 0), (1, 0)]
        result = sl.get_ccw_vertices(line1, line2)
        self.assertEqual(result, [(1, 1), (0, 1), (0, 0), (1, 0), (1, 1)])

    def test_ccw_line2_cw(self):
        """
            line1 (0, 1) <- (1, 1)
            line2 (0, 0) <- (1, 0)
        """
        line1 = [(1, 1), (0, 1)]
        line2 = [(1, 0), (0, 0)]
        result = sl.get_ccw_vertices(line1, line2)
        self.assertEqual(result, [(1, 1), (0, 1), (0, 0), (1, 0), (1, 1)])

    def test_ccw_line1_cw(self):
        """
            line1 (0, 1) -> (1, 1)
            line2 (0, 0) -> (1, 0)
        """
        line1 = [(0, 1), (1, 1)]
        line2 = [(0, 0), (1, 0)]
        result = sl.get_ccw_vertices(line1, line2)
        self.assertEqual(result, [(0, 1), (0, 0), (1, 0), (1, 1), (0, 1)])

    def test_ccw_both_cw(self):
        """
            line1 (0, 1) -> (1, 1)
            line2 (0, 0) <- (1, 0)
        """
        line1 = [(0, 1), (1, 1)]
        line2 = [(1, 0), (0, 0)]
        result = sl.get_ccw_vertices(line1, line2)
        self.assertEqual(result, [(0, 1), (0, 0), (1, 0), (1, 1), (0, 1)])


class TestLaplace(unittest.TestCase):

    def test_generate_laplace_field_mesh_values(self):
        pia = [(1, 1), (0, 1)]
        wm = [(0, 0), (1, 0)]

        (u, udot, mesh_coords, mesh_values, mesh_gradients
         ) = sl.generate_laplace_field(pia, wm, mesh_res=1)

        assert np.allclose(mesh_values, [1, 0, 0, 1, 0, 0.5, 1, 0.5])

    def test_generate_laplace_field_mesh_gradients(self):
        pia = [(1, 1), (0, 1)]
        wm = [(0, 0), (1, 0)]

        (u, udot, mesh_coords, mesh_values, mesh_gradients
         ) = sl.generate_laplace_field(pia, wm, mesh_res=1)

        assert np.allclose(mesh_gradients, [[0, 1] for i in range(8)])
