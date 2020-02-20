import sys
sys.path.insert(0, "../")

from io import StringIO
import requests
from neuron_morphology.swc_io import morphology_from_swc
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.features.default_features import default_features
import neuron_morphology.feature_extractor.feature_writer as fw
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('args', nargs='+')
arguments = parser.parse_args()

input = arguments.args[0] # .swc
output_h5 = arguments.args[1] # .h5
output_csv = arguments.args[2] # .csv

test_data = Data(morphology_from_swc(input))

fe = FeatureExtractor()
for feature in default_features:
    fe.register_features([feature])

feature_extraction_run = fe.extract(test_data)

features = feature_extraction_run.results

features_writer = fw.FeatureWriter(output_h5, output_csv)
features_writer.add_run(input, feature_extraction_run.serialize())
features_writer.write_table()
