import sys
import unittest

import numpy as np


try:
    import dolfinx
    from neuron_morphology.transforms import streamline as sl

    has_dolfinx = True
except ImportError:
    has_dolfinx = False


@unittest.skipIf(
    not has_dolfinx, "streamline calculation requires conda-installed fenics-dolfinx"
)
class TestLaplace(unittest.TestCase):
    def test_generate_laplace_field_mesh_values(self):
        pia = [(1, 1), (0, 1)]
        wm = [(0, 0), (1, 0)]

        (
            u,
            grad_u,
            mesh,
            mesh_coords,
            mesh_values,
            mesh_gradients,
        ) = sl.generate_laplace_field(pia, wm, mesh_res=1)
        print(mesh_coords)
        assert np.allclose(mesh_values, mesh_coords[:,1])

    def test_generate_laplace_field_mesh_gradients(self):
        pia = [(1, 1), (0, 1)]
        wm = [(0, 0), (1, 0)]

        (
            u,
            grad_u,
            mesh,
            mesh_coords,
            mesh_values,
            mesh_gradients,
        ) = sl.generate_laplace_field(pia, wm, mesh_res=1)
        print(mesh_coords)
        assert np.allclose(mesh_gradients, [[0, 1] for i in range(len(mesh_gradients))])
