import unittest

from neuron_morphology.feature_extractor.utilities import unnest


class TestUnnest(unittest.TestCase):


    def test_simple(self):

        nested = {"a": {"b": 1}, "c": 2}
        obt = unnest(nested)

        self.assertSetEqual({"a.b", "c"}, set(obt.keys()))