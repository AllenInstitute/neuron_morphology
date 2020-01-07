import unittest
from tests.objects import test_morphology_large
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.features.default_features import default_features
from neuron_morphology.feature_extractor.data import Data


class TestDefault(unittest.TestCase):

    fe = FeatureExtractor()

    for feature in default_features:
        fe.register_features([feature])

    data = Data(test_morphology_large())
    feature_extraction_run = fe.extract(data)
    results = feature_extraction_run.results

    pass
