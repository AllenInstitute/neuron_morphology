import sys
sys.path.insert(0, "../")

from io import StringIO
import requests
from neuron_morphology.swc_io import morphology_from_swc
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.feature_extractor import FeatureExtractor
from neuron_morphology.features.default_features import default_features
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('args', nargs='+')
arguments = parser.parse_args()

input = arguments.args[0] # .swc
output = arguments.args[1] # .json

test_data = Data(morphology_from_swc(input))

fe = FeatureExtractor()
for feature in default_features:
    fe.register_features([feature])

feature_extraction_run = fe.extract(test_data)

features = feature_extraction_run.results

#
#with open(output, 'w') as outfile:
#    json.dump(features, outfile)


print(features)

with open(output,'w') as filehandle:
    filehandle.writelines("%s\n" % feature for feature in features)
