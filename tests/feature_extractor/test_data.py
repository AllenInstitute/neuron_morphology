import unittest

from neuron_morphology.feature_extractor.data import Data, get_morphology
from neuron_morphology.morphology_builder import MorphologyBuilder

class TestData(unittest.TestCase):

    def setUp(self):
        self.morphology = (
            MorphologyBuilder()
                .root()
                    .axon()
                        .axon()
                            .axon()
                .build()
        )

    def test_additional_data(self):
        obt = Data(self.morphology, a=1, b=2)
        self.assertEqual(obt.a, 1)
        self.assertEqual(obt.b, 2)
        self.assertEqual(len(obt.morphology.nodes()), 4)
    
    def test_get_morphology(self):
        aa = get_morphology(Data(self.morphology))
        bb = get_morphology(self.morphology)

        self.assertEqual(aa.__class__.__name__, "Morphology")
        self.assertEqual(bb.__class__.__name__, "Morphology")

    def test_hash(self):
        dat = Data(self.morphology)
        self.assertEqual({dat}, {dat})