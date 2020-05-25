import os
import subprocess as sp
import unittest
import shutil
import tempfile

import numpy as np
import h5py

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.swc_io import morphology_to_swc
from neuron_morphology.transforms.tilt_correction.compute_tilt_correction import (
    get_tilt_correction, run_tilt_correction, CCF_SHAPE, CCF_RESOLUTION)
from neuron_morphology.transforms.affine_transform import AffineTransform

import allensdk.core.json_utilities as ju


class TestTiltCorrection(unittest.TestCase):
    def setUp(self):

        self.morphology = (
            MorphologyBuilder()
                .root(1, 2, 3)
                    .axon(0, 2, 3)
                        .build()
        )

        self.test_dir = tempfile.mkdtemp()

        self.swc_path = os.path.join(self.test_dir, '123.swc')
        morphology_to_swc(self.morphology, self.swc_path)

        self.marker_path = os.path.join(self.test_dir, '123.marker')
        with open(self.marker_path, 'w') as f:
            f.write("##x,y,z,radius,shape,name,comment, color_r,color_g,color_b\n"
                    "1.0,2.0,2.5,0.0,0,30,0,255, 255, 255\n"
                    "0.0,2.0,3.0,0.0,0,20,0,255, 255, 255")

        self.slice_transform_list = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        self.slice_transform = AffineTransform.from_list(self.slice_transform_list)
        self.slice_image_flip = True

        self.soma_marker = {'x': 1, 'y': 2, 'z': 0}
        self.soma_voxel = (400, 400, 1120)

        self.ccf_soma_location = [self.soma_voxel[0] * CCF_RESOLUTION,
                                  self.soma_voxel[1] * CCF_RESOLUTION,
                                  self.soma_voxel[2] * CCF_RESOLUTION
                                  ]
        self.csl_dict = dict(zip(['x', 'y', 'z'], self.ccf_soma_location))

        # Streamline is on z+, so should result in tilt of np.pi / 2
        self.closest_path = np.asarray([400 * np.ones((20,), dtype='i'),
                                        400 * np.ones((20,), dtype='i'),
                                        np.arange(1120, 1140, dtype='i')])

        self.ccf_path = os.path.join(self.test_dir, 'paths.h5')
        path = np.ravel_multi_index(self.closest_path, CCF_SHAPE)
        with h5py.File(self.ccf_path, 'w') as f:
            f.create_dataset("view lookup", (1, ), dtype='i', data=0)
            f.create_dataset("paths", (1, 20), dtype='i', data=path)

        self.output_json_path = os.path.join(self.test_dir, 'output.json')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_tilt_correction(self):
        tilt = get_tilt_correction(self.morphology,
                                   self.soma_voxel,
                                   self.slice_transform.affine,
                                   self.closest_path)
        self.assertAlmostEqual(tilt, -np.pi / 2)

    def test_run_tilt_correction(self):
        (tilt, transform) = run_tilt_correction(self.morphology,
                                                self.soma_marker,
                                                self.csl_dict,
                                                self.slice_transform,
                                                self.slice_image_flip,
                                                self.ccf_path)
        self.assertAlmostEqual(tilt, -np.pi / 2)

    def test_tilt_correction_end_to_end(self):
        input = {'swc_path': self.swc_path,
                 'marker_path': self.marker_path,
                 'ccf_soma_location': self.ccf_soma_location,
                 'slice_transform_list': self.slice_transform_list,
                 'slice_image_flip': self.slice_image_flip,
                 'ccf_path': self.ccf_path,
                 'output_json': self.output_json_path}
        cmd = ['python', '-m',
               'neuron_morphology.transforms.tilt_correction.compute_tilt_correction']
        for key, value in input.items():
            cmd.append(f'--{key}')
            cmd.append(f'{value}')

        sp.check_call(cmd)

        outputs = ju.read(self.output_json_path)
        self.assertAlmostEqual(outputs['tilt_correction'], -np.pi / 2)

        aff_t = AffineTransform.from_dict(outputs['tilt_transform_dict'])
        morph_t = aff_t.transform_morphology(self.morphology)

        axon = morph_t.node_by_id(1)
        self.assertAlmostEqual(axon['x'], 0)
        self.assertAlmostEqual(axon['y'], 3)
        self.assertAlmostEqual(axon['z'], -2)