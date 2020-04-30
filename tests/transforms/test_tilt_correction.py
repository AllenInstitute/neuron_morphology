import os
import subprocess as sp
import unittest
import shutil
import tempfile

import numpy as np

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.swc_io import morphology_to_swc
from neuron_morphology.transforms.tilt_correction.compute_tilt_correction import (
    get_tilt_correction)
from neuron_morphology.transforms.affine_transform import AffineTransform

import allensdk.core.json_utilities as ju


class TestScaleCorrection(unittest.TestCase):
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
                    "1.0,2.0,3.5,0.0,0,30,0,255, 255, 255\n"
                    "0.0,2.0,3.0,0.0,0,20,0,255, 255, 255")

        self.soma_marker = {'x': 1.0, 'y': 2.0, 'z': 3.5}

        self.slice_transform = 

        self.streamlines = 

        self.ccf_path = 


        
        self.output_json_path = os.path.join(self.test_dir, 'output.json')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_tilt_correction(self):
        tilt = get_tilt_correction(self.morphology,
                                   self.soma_marker,
                                   self.slice_transform,
                                   self.streamlines)
        self.assertAlmostEqual(tilt, )

    def test_scale_correction_end_to_end(self):
        input = {'swc_path': self.swc_path,
                 'marker_path': self.marker_path,
                 'slice_transform_list': self.slice_transform_list,
                 'ccf_path': self.ccf_path,
                 'output_json': self.output_json_path}
        cmd = ['python', '-m',
               'neuron_morphology.transforms.tilt_correction.compute_tilt_correction']
        for key, value in input.items():
            cmd.append(f'--{key}')
            cmd.append(f'{value}')

        sp.check_call(cmd)

        outputs = ju.read(self.output_json_path)
        self.assertAlmostEqual(outputs['tilt_correction'], )

        aff_t = AffineTransform.from_dict(outputs['tilt_transform_dict'])
        morph_t = aff_t.transform_morphology(self.morphology)

        axon = morph_t.node_by_id(1)
        self.assertAlmostEqual(axon['x'], 0)
        self.assertAlmostEqual(axon['y'], 2)
        self.assertAlmostEqual(axon['z'], 6)