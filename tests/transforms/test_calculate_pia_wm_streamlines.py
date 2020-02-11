import os
import sys
import subprocess as sp
import unittest
import shutil
import tempfile
import xarray as xr
import numpy as np

try:
    import fenics
except ImportError:
    pass

@unittest.skipIf('fenics' not in sys.modules,
                 'streamline calculation requires conda-installed fenics')
class TestRunPiaWmStreamlines(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.input = {
            'pia_path_str': '120,100,0,100',
            'wm_path_str': '20,0,100,0',
            'soma_path_str': '50,50',
            'output_dir': self.test_dir,
            'output_json': os.path.join(self.test_dir, 'output.json')
        }
        self.output = {
            'input': self.input,
            'depth_field_file': os.path.join(self.test_dir, 'depth_field.nc'),
            'gradient_field_file': os.path.join(self.test_dir,
                                                'gradient_field.nc'),
        }

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_end_to_end(self):
        cmd = ['python', '-m',
               'neuron_morphology.transforms.pia_wm_streamlines.'
               'calculate_pia_wm_streamlines']
        for key, value in self.input.items():
            cmd.append(f'--{key}')
            cmd.append(f'{value}')

        sp.check_call(cmd)

        depth_file = os.path.join(self.test_dir, 'depth_field.nc')
        with xr.open_dataarray(depth_file) as da:
            self.assertEqual(len(da.x), 122)
            self.assertAlmostEqual(round(float(da[50, 50]), 5), 0.52788)
            self.assertEqual(np.isnan(da[0, 0]), True)

        gradient_file = os.path.join(self.test_dir, 'gradient_field.nc')
        with xr.open_dataarray(gradient_file) as dg:
            self.assertEqual(len(dg.y), 102)
            x = dg[50, 70].values
            x = x / np.linalg.norm(x)
            assert np.allclose(x[1], 1, atol=1e-2)
            self.assertEqual(np.all(np.isnan(dg[0, 0])), True)
