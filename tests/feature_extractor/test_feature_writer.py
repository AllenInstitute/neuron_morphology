import unittest
import shutil
import tempfile
import os

import numpy as np
import pandas as pd

from neuron_morphology.feature_extractor.feature_extraction_run import \
    FeatureExtractionRun
from neuron_morphology.feature_extractor.feature_writer import FeatureWriter
from neuron_morphology.features.layer.layer_histogram import \
    EarthMoversDistanceResult, LayerHistogram


class TestFeatureWriter(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

        self.heavy_path = os.path.join(self.tmpdir, "heavy.h5")
        self.table_path = os.path.join(self.tmpdir, "table.csv")

        self.outputs = {
            "a": {"results": {"fish": "salmon", "fowl": "hawk"}},
            "b": {"results": {"fish": "pike", "mammal": { "marsupial": "koala"} } }
        }
        self.expected_output_table = pd.DataFrame(
            {
                "fish": ["salmon", "pike"], 
                "fowl": ["hawk", None], 
                "mammal.marsupial": [None, "koala"]
            },
            index=pd.Index(name="reconstruction_id", data=["a", "b"])
        )

    def tearDown(self):
        shutil.rmtree(self.tmpdir)
    
    def test_add_run(self):

        run = FeatureExtractionRun("data!")
        run.results = {"a": 1, "b": 2}

        writer = FeatureWriter(self.heavy_path, self.table_path)
        writer.add_run("test", run.serialize())
        self.assertEqual(writer.output["test"]["results"]["a"], 1)

    def test_process_feature_emd(self):

        writer = FeatureWriter(self.heavy_path, self.table_path)

        obt = writer.process_feature(
            "foo", 
            "a.b.earth_movers_distance", 
            EarthMoversDistanceResult(10, "0.1")
        )

        self.assertEqual(obt["interpretation"], "1")
        self.assertEqual(obt["result"], 10)

    def test_add_layer_histogram(self):

        writer = FeatureWriter(self.heavy_path, self.table_path)
        writer.add_layer_histogram(
            "fish", "fowl", LayerHistogram([1, 2, 3], [4, 5, 6]))

        self.assertTrue(writer.has_heavy)
        assert np.allclose(
            writer.heavy_file["fish/fowl/counts"][:],
            [1, 2, 3]
        )

    def test_build_output_table(self):
        writer = FeatureWriter(self.heavy_path, self.table_path)
        writer.output = self.outputs
        table = writer.build_output_table()
        pd.testing.assert_frame_equal(
            table, 
            self.expected_output_table,
            check_like=True
        )

    def test_write_output_table(self):
        writer = FeatureWriter(self.heavy_path, self.table_path)
        writer.output = self.outputs
        writer.write_table()

        obt = pd.read_csv(self.table_path)
        obt.set_index("reconstruction_id", inplace=True)

        pd.testing.assert_frame_equal(
            obt, 
            self.expected_output_table,
            check_like=True
        )

