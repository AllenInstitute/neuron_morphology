import sys
import unittest

import numpy as np

try:
    import fenics
    from neuron_morphology.transforms import streamline as sl
except ImportError:
    pass

@unittest.skipIf('fenics' not in sys.modules,
                 'streamline calculation requires conda-installed fenics')
class TestLaplace(unittest.TestCase):

    def test_generate_laplace_field_mesh_values(self):
        pia = [(1, 1), (0, 1)]
        wm = [(0, 0), (1, 0)]

        (u, grad_u, mesh, mesh_coords, mesh_values, mesh_gradients
         ) = sl.generate_laplace_field(pia, wm, mesh_res=1)

        assert np.allclose(mesh_values, [1, 0, 0, 1, 0, 0.5, 1, 0.5])

    def test_generate_laplace_field_mesh_gradients(self):
        pia = [(1, 1), (0, 1)]
        wm = [(0, 0), (1, 0)]

        (u, grad_u, mesh, mesh_coords, mesh_values, mesh_gradients
         ) = sl.generate_laplace_field(pia, wm, mesh_res=1)

        assert np.allclose(mesh_gradients, [[0, 1] for i in range(8)])
