import unittest
import tempfile
import shutil
import os
import subprocess as sp
import json
import os

import pandas as pd
import numpy as np
import h5py
import pytest

import neuron_morphology.feature_extractor.__main__ as main
from neuron_morphology.swc_io import write_swc
from neuron_morphology.constants import (
    SOMA, APICAL_DENDRITE, BASAL_DENDRITE, AXON
)
from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.features.layer.layered_point_depths import \
    LayeredPointDepths


TIMEOUT = int(os.getenv("TIMEOUT", "60"))


def nodes():
    return (
        MorphologyBuilder()
            .root()
                .axon()
                    .axon()
                        .axon().up(3)
                .apical_dendrite()
                    .apical_dendrite()
                        .apical_dendrite().up()
                        .apical_dendrite()
            .nodes
    )


class TestRun(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

        _nodes = nodes()
        self.first_path = os.path.join(self.tmpdir, "first.swc")
        write_swc(pd.DataFrame(nodes()), self.first_path)
        self.second_path = os.path.join(self.tmpdir, "second.swc")
        write_swc(pd.DataFrame(nodes()), self.second_path)

        self.lpd_path = os.path.join(self.tmpdir, "layered_point_depths.csv")
        LayeredPointDepths(
            ids=np.arange(8)[::-1],
            layer_name=["2", "2", "wm", "wm", "2", "1", "1", "1"],
            depth=[200, 230, 260, 290, 60, 40, 30, 20],
            local_layer_pia_side_depth=[50, 50, 250, 250, 50, 0, 0, 0],
            local_layer_wm_side_depth=[250, 250, np.nan, np.nan, 250, 50, 50, 50],
            point_type=[node["type"] for node in _nodes]
        ).to_csv(self.lpd_path)

        self.heavy_output_path = os.path.join(self.tmpdir, "heavy.h5")
        input_json_data = {
            "heavy_output_path": self.heavy_output_path,
            "reconstructions": [
                {
                    "swc_path": self.first_path,
                    "identifier": "first",
                    "layered_point_depths_path": self.lpd_path
                },
                {
                    "swc_path": self.second_path,
                    "identifier": "second"
                }
            ],
            "global_parameters": {
                "reference_layer_depths": {
                    "names": ["1", "2", "wm"],
                    "boundaries": [0, 100, 200, 300]
                }
            }
        }
        self.input_json_path = os.path.join(self.tmpdir, "input.json")
        self.output_json_path = os.path.join(self.tmpdir, "output.json")
        with open(self.input_json_path, "w") as input_file:
            json.dump(input_json_data, input_file)

        sp.check_call([
            "python", "-m", "neuron_morphology.feature_extractor", 
            "--input_json", self.input_json_path,
            "--output_json", self.output_json_path
            ],
            timeout=TIMEOUT)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    # we are invoking our tests in ci using pytest, resulting in this hideous 
    # mixing of frameworks - unittest can also skipIf but the directive is not 
    # respected by pytest collector
    @pytest.mark.skipif(TIMEOUT == 0, reason="potentially long-running test")
    def test_run(self):

        with open(self.output_json_path, "r") as output_file:
            obtained = json.load(output_file)

        first_results = obtained["results"]["first"]["results"]
        second_results = obtained["results"]["second"]["results"]

        self.assertEqual(first_results["axon.num_tips"], 1)
        self.assertEqual(
            first_results
                ["axon.apical_dendrite.earth_movers_distance.2"]
                ["result"],
            17.0
        )
        self.assertEqual(
            first_results
                ["axon.apical_dendrite.earth_movers_distance.2"]
                ["interpretation"],
            "BothPresent"
        )

        self.assertNotIn(
            "axon.apical_dendrite.earth_movers_distance.2", second_results)

    @pytest.mark.skipif(TIMEOUT == 0, reason="potentially long-running test")
    def test_run_heavy_out(self):
        expected_counts = np.zeros(20)
        expected_counts[18] = 1

        with h5py.File(self.heavy_output_path, "r") as hf:
            counts = hf["first/axon.normalized_depth_histogram.2/counts"][:]
            assert np.allclose(counts, expected_counts)
