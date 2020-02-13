import unittest

import math
import numpy as np
import xarray as xr
from neuron_morphology.angle.compute_angle import ComputeAngle

class TestUprightAngle(unittest.TestCase):
    def setUp(self):
        # input gradient in xarray format
        dx = np.array([0.219,0.254,0.335,0.477,0.776,0.165,\
               0.181,np.NaN,0.238,0.276,0.332,0.422,\
               0.542,0.706,0.856,np.NaN,0.203,0.224,\
               0.25,0.283,np.NaN,0.385,0.463,0.556,\
               0.666,0.743,0.785,0.246,0.236,0.256,\
               0.279,0.316,0.367,0.421,0.491,0.569])

        dx = dx.reshape(6,6)

        dy = np.array([-0.921, np.NaN,-1.105,-1.237,-1.324,-0.692,\
                    -0.735,-0.777,np.NaN,-0.88,-0.941,-1.006,\
                    -1.062,-1.048,-0.925,-0.628,-0.674,-0.713,\
                    -0.748,-0.792,-0.829,-0.87,np.NaN,-0.942,\
                    -0.928,-0.879,-0.842,-0.643,-0.665,-0.69,\
                    -0.716,-0.744,-0.772,-0.808,-0.83,-0.843])

        dy = dy.reshape(6,6)

        x = np.array([-35, -20, -5, 5, 20, 35])
        y = np.array([-35, -20, -5, 5, 20, 35])

        grad_data = np.empty((6,6,2))

        grad_data[:,:,0] = dx
        grad_data[:,:,1] = dy

        self.gradient = xr.DataArray(grad_data, dims=['x','y','dim'], coords={'x': x, 'y': y, 'dim': ['dx','dy']})

    def test_upright_angle(self):
        upright_angle = ComputeAngle().calculate_upright_angle(self.gradient,[0,0])
        self.assertAlmostEqual(upright_angle, 2.585, 3)

