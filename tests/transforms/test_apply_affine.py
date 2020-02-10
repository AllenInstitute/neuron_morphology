import os
import subprocess as sp
import unittest
import shutil
import tempfile
import numpy as np
from neuron_morphology.swc_io import morphology_to_swc, morphology_from_swc
from neuron_morphology.morphology_builder import MorphologyBuilder


class TestRunPiaWmStreamlines(unittest.TestCase):

    def setUp(self):
        """
        y+
        |
        P
        ^
        P
        ^
        S > A > A - x+
        """
        self.morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .axon(1, 0, 0)
                        .axon(2, 0, 0).up(2)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                .build()
            )
        self.transformed_vector = [[0, 0, 0],
                                   [0.5, np.sqrt(3) / 2, 0],
                                   [1, np.sqrt(3), 0],
                                   [-np.sqrt(3)/2, 0.5, 0],
                                   [-np.sqrt(3), 1, 0]]

        self.test_dir = tempfile.mkdtemp()
        self.input_swc_name = 'input.swc'
        self.output_swc_name = 'transformed.swc'
        morphology_to_swc(self.morphology, os.path.join(self.test_dir, self.input_swc_name))

        rad = 60 * np.pi / 180
        c = np.cos(rad)
        s = np.sin(rad)
        self.input = {
            'affine_list': f'[{c},{-s},0,{s},{c},0,0,0,1,0,0,0]',
            'input_swc': os.path.join(self.test_dir, self.input_swc_name),
            'output_swc': os.path.join(self.test_dir, self.output_swc_name),
            'output_json': os.path.join(self.test_dir, 'output.json')
        }
        self.output = {
            'input': self.input,
            'transformed_swc': os.path.join(self.test_dir, self.output_swc_name),
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_end_to_end(self):
        cmd = ['python', '-m',
               'neuron_morphology.transforms.affine_transformer.'
               'apply_affine_transform']
        for key, value in self.input.items():
            cmd.append(f'--{key}')
            cmd.append(f'{value}')

        sp.check_call(cmd)

        transformed_swc = os.path.join(self.test_dir, self.output_swc_name)
        tf_morph = morphology_from_swc(transformed_swc)

        for node in tf_morph.nodes():
            assert np.allclose([node['x'], node['y'], node['z']],
                               self.transformed_vector[node['id']])
