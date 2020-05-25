import os
import subprocess as sp
import unittest
import shutil
import tempfile

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.swc_io import morphology_to_swc
from neuron_morphology.transforms.scale_correction.compute_scale_correction import (
    estimate_scale_correction, run_scale_correction)
from neuron_morphology.transforms.affine_transform import AffineTransform

import allensdk.core.json_utilities as ju


class TestScaleCorrection(unittest.TestCase):
    def setUp(self):

        self.morphology = (
            MorphologyBuilder()
                .root(1, 2, 3, radius=1.3)
                    .axon(0, 2, 100, radius=0.4)
                        .build()
        )
        self.max_morphology = (
            MorphologyBuilder()
                .root(1, 2, 3)
                    .axon(0, 2, 353)
                        .build()
        )
        self.soma_depth = 1.0
        self.cut_thickness = 350

        self.test_dir = tempfile.mkdtemp()

        self.swc_path = os.path.join(self.test_dir, '123.swc')
        morphology_to_swc(self.morphology, self.swc_path)

        self.marker_path = os.path.join(self.test_dir, '123.marker')
        with open(self.marker_path, 'w') as f:
            f.write("##x,y,z,radius,shape,name,comment, color_r,color_g,color_b\n"
                    "1.0,2.0,3.5,0.0,0,30,0,255, 255, 255\n"
                    "0.0,2.0,3.0,0.0,0,20,0,255, 255, 255")

        self.soma_marker_z = 3.5
        self.output_json_path = os.path.join(self.test_dir, 'output.json')

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_scale_correction(self):
        scale = estimate_scale_correction(self.morphology,
                                     self.soma_depth,
                                     self.soma_marker_z,
                                     self.cut_thickness)
        self.assertAlmostEqual(scale, 2.0)
    def test_scale_correction_max(self):
        scale = estimate_scale_correction(self.max_morphology,
                                     self.soma_depth,
                                     self.soma_marker_z,
                                     self.cut_thickness)
        self.assertAlmostEqual(scale, 1.0)

    def test_scale_correction_end_to_end(self):
        input = {'swc_path': self.swc_path,
                 'marker_path': self.marker_path,
                 'soma_depth': self.soma_depth,
                 'cut_thickness': self.cut_thickness,
                 'output_json': self.output_json_path}
        cmd = ['python', '-m',
               'neuron_morphology.transforms.scale_correction.compute_scale_correction']
        for key, value in input.items():
            cmd.append(f'--{key}')
            cmd.append(f'{value}')

        sp.check_call(cmd)

        outputs = ju.read(self.output_json_path)
        self.assertAlmostEqual(outputs['scale_correction'], 2.0)

        aff_t = AffineTransform.from_dict(outputs['scale_transform'])
        morph_t = aff_t.transform_morphology(self.morphology,
                                             scale_radius=False)

        axon = morph_t.node_by_id(1)
        self.assertAlmostEqual(axon['x'], 0)
        self.assertAlmostEqual(axon['y'], 2)
        self.assertAlmostEqual(axon['z'], 200)
        self.assertAlmostEqual(axon['radius'], 0.4)

    def test_run_scale_correction(self):

        inputs = {
            "morphology": self.morphology,
            "soma_marker_z": self.soma_marker_z,
            "soma_depth": self.soma_depth,
            "cut_thickness": self.cut_thickness,
        }

        expected = {
            'scale_transform':
                {'tvr_00': 1.0,
                 'tvr_01': 0.0,
                 'tvr_02': 0.0,
                 'tvr_03': 0.0,
                 'tvr_04': 1.0,
                 'tvr_05': 0.0,
                 'tvr_06': 0.0,
                 'tvr_07': 0.0,
                 'tvr_08': 2.0,
                 'tvr_09': 0.0,
                 'tvr_10': 0.0,
                 'tvr_11': 0.0,
                 },
            'scale_correction': 2.0
        }

        obtained = run_scale_correction(**inputs)
        obtained.pop("morphology_scaled")

        print(expected)
        print(obtained)
        assert expected == obtained
