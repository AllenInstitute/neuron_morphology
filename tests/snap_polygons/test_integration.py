from unittest import TestCase, skipIf
import subprocess as sp
import os
import tempfile
import shutil
import json

from dictdiffer import diff


class SnapPolygonsIntegration(TestCase):

    @skipIf(
        os.environ.get("TEST_INTEGRATION", "false") != "true",
        "The integration tests can take a while - must opt in!"
    )
    def test_integration(self):
        data_root = os.path.join(os.path.dirname(__file__), "data")
        cases = [
            ["678492000_inputs.json", "678492000_outputs.json"],
            ["680352737_inputs.json", "680352737_outputs.json"],
            ["735355641_inputs.json", "735355641_outputs.json"],
            ["839050458_inputs.json", "839050458_outputs.json"]
        ]

        tmpdir = tempfile.mkdtemp()

        for in_fname, out_fname in cases:
            with self.subTest():
                full_in_json_path = os.path.join(data_root, in_fname)
                full_out_json_path = os.path.join(tmpdir, out_fname)
                full_expected_path = os.path.join(data_root, out_fname)

                sp.check_call([
                    "python", "-m", "neuron_morphology.snap_polygons",
                    "--input_json", full_in_json_path,
                    "--output_json", full_out_json_path
                ])

                with open(full_out_json_path, "r") as out_json:
                    obtained = json.load(out_json)
                with open(full_expected_path, "r") as expected_json:
                    expected = json.load(expected_json)

                difference = diff(expected, obtained)
                self.assertEqual(list(difference), [])

        shutil.rmtree(tmpdir)
