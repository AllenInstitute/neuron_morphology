import os
import sys
import subprocess as sp
import unittest
import shutil
import tempfile

import xarray as xr
import numpy as np

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.swc_io import morphology_to_swc
from neuron_morphology.transforms.upright_angle.compute_angle import (
    get_upright_angle)
from neuron_morphology.transforms.affine_transform import AffineTransform

import allensdk.core.json_utilities as ju

class TestUprightAngle(unittest.TestCase):
    def setUp(self):
        # input gradient in xarray format
        # up is negative x, so expected rotation is - pi / 2
        dx = -np.ones((6, 6))
        dy = np.zeros((6, 6))

        x = np.array([-35, -20, -5, 5, 20, 35])
        y = np.array([-35, -20, -5, 5, 20, 35])

        grad_data = np.empty((6,6,2))

        grad_data[:,:,0] = dx
        grad_data[:,:,1] = dy

        self.morphology = (
            MorphologyBuilder()
                .root(1, 2, 3)
                    .axon(0,2,3)
                        .build()
        )
        self.gradient = xr.DataArray(grad_data, dims=['x','y','dim'], coords={'x': x, 'y': y, 'dim': ['dx','dy']})

        self.test_dir = tempfile.mkdtemp()
        self.gradient_path = os.path.join(self.test_dir, 'gradient.nc')
        self.gradient.to_netcdf(self.gradient_path)

        self.swc_path = os.path.join(self.test_dir, '123.swc')
        morphology_to_swc(self.morphology, self.swc_path)

        self.output_json_path = os.path.join(self.test_dir, 'output.json')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_upright_angle(self):
        upright_angle = get_upright_angle(self.gradient, [0,0,0])
        self.assertAlmostEqual(upright_angle, -np.pi / 2, 3)

    def test_upright_end_to_end(self):
        input = {'gradient_path': self.gradient_path,
                 'node': '[0, 0, 0]',
                 'swc_path': self.swc_path,
                 'output_json': self.output_json_path}
        cmd = ['python', '-m',
               'neuron_morphology.transforms.upright_angle.compute_angle']
        for key, value in input.items():
            cmd.append(f'--{key}')
            cmd.append(f'{value}')

        sp.check_call(cmd)

        outputs = ju.read(self.output_json_path)
        self.assertAlmostEqual(outputs['upright_angle'], -np.pi / 2, 3)

        aff_t = AffineTransform.from_dict(outputs['upright_transform_dict'])
        morph_t = aff_t.transform_morphology(self.morphology)

        axon = morph_t.node_by_id(1)
        self.assertAlmostEqual(axon['x'], 1)
        self.assertAlmostEqual(axon['y'], 3)
        self.assertAlmostEqual(axon['z'], 3)
