import unittest
import tempfile
import shutil
import os

import pandas as pd

import neuron_morphology.feature_extractor.__main__ as main
from neuron_morphology.swc_io import write_swc
from neuron_morphology.constants import (
    SOMA, APICAL_DENDRITE, BASAL_DENDRITE, AXON
)


def nodes():
    return [
        {
            "id": 0,
            "parent": -1,
            "type": SOMA,
            "x": 0,
            "y": 0,
            "z": 100,
            "radius": 1
        },
        {
            "id": 1,
            "parent": 0,
            "type": AXON,
            "x": 0,
            "y": 0,
            "z": 101,
            "radius": 1
        },
        {
            "id": 2,
            "parent": 0,
            "type": APICAL_DENDRITE,
            "x": 0,
            "y": 0,
            "z": 102,
            "radius": 1
        },
        {
            "id": 3,
            "parent": 1,
            "type": AXON,
            "x": 0,
            "y": 0,
            "z": 110,
            "radius": 1
        },                
        {
            "id": 4,
            "parent": 3,
            "type": AXON,
            "x": 0,
            "y": 0,
            "z": 140,
            "radius": 1 
        },                
        {
            "id": 5,
            "parent": 3,
            "type": AXON,
            "x": 0,
            "y": 0,
            "z": 130,
            "radius": 1 
        },                
        {
            "id": 6,
            "parent": 5,
            "type": AXON,
            "x": 0,
            "y": 0,
            "z": 135,
            "radius": 1 
        },       
        {
            "id": 7,
            "parent": 5,
            "type": AXON,
            "x": 0,
            "y": 0,
            "z": 136,
            "radius": 1 
        },     
        {
            "id": 8,
            "parent": 2,
            "type": APICAL_DENDRITE,
            "x": 0,
            "y": 0,
            "z": 125,
            "radius": 1 
        },
        {
            "id": 9,
            "parent": 8,
            "type": APICAL_DENDRITE,
            "x": 0,
            "y": 0,
            "z": 126,
            "radius": 1 
        },
        {
            "id": 10,
            "parent": 8,
            "type": APICAL_DENDRITE,
            "x": 0,
            "y": 0,
            "z": 127,
            "radius": 1 
        },
    ]



class TestIo(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

        self.outputs = {"results": {
            "a": {"results": {"fish": "salmon", "fowl": "hawk"}},
            "b": {"results": {"fish": "pike", "mammal": { "marsupial": "koala"} } }
        }}
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

    def test_load_data(self):
        path = os.path.join(self.tmpdir, "test.swc")
        write_swc(pd.DataFrame(nodes()), path)

        obtained = main.load_data(path)
        self.assertEqual(
            len(obtained.morphology.nodes()),
            11
        )

    def test_build_output_table(self):
        table = main.build_output_table(self.outputs)
        pd.testing.assert_frame_equal(
            table, 
            self.expected_output_table,
            check_like=True
        )

    def test_write_additional_outputs(self):
        path = os.path.join(self.tmpdir, "table.csv")
        main.write_additional_outputs(self.outputs, path)

        obt = pd.read_csv(path)
        obt.set_index("reconstruction_id", inplace=True)

        pd.testing.assert_frame_equal(
            obt, 
            self.expected_output_table,
            check_like=True
        )