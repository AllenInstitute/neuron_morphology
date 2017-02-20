import sys
import neuron_morphology.swc as swc
from neuron_morphology.features.feature_extractor import *

from pkg_resources import resource_filename  # @UnresolvedImport

#sys.path.append("/home/keithg/allen/allensdk/")
#from allensdk.core import json_utilities as json

########################################################################

test_file = "Ctgf-2A-dgCre-D_Ai14_BT_-245170.06.06.01_539748835_m_pia.swc"
pct_tolerance = 0.1

expected_values = {}
expected_values["first_bifurcation_moment_x"] =  145.78
expected_values["first_bifurcation_moment_y"] = -11.763
expected_values["first_bifurcation_moment_z"] =  2.7767
expected_values["bifurcation_stdev_x"] =  54.740
expected_values["bifurcation_stdev_y"] =  63.946
expected_values["bifurcation_stdev_z"] =  10.546

# moment values validated against manually calculated non-weighted
#   moments.  algorithm then switched back to using weighted
#   moments. the numbers were similar and are encoded here
expected_values["first_compartment_moment_x"] =  169.98
expected_values["first_compartment_moment_y"] =  11.343
expected_values["first_compartment_moment_z"] =  16.854
expected_values["compartment_stdev_x"] =  70.534
expected_values["compartment_stdev_y"] =  109.26
expected_values["compartment_stdev_z"] =  24.917

expected_values["width"] = 313.60
expected_values["depth"] = 122.85
expected_values["height"] = 424.47

expected_values["num_outer_bifurcations"] = 3

# manual calculation (with known error ~1%) yielded 0.7329. calculated
#   value was .7249, in range of expected error. going with calculated value
expected_values["early_branch"] = .7249

# don't check for relative soma depth -- this is a value pulled from
#   the database and it isn't computed in the feature extractor
#expected_values["relative_soma_depth"] = 0.985589824334

#############################################

# the below fields were previuosly validated by comparing w/ the output
#   of vaa3d, and explaining differences. Most differences from vaa3d
#   output relate to vaa3d including the soma in several calculations
#   about the morphology (eg, including the soma radius in the length
#   of a branch, or including the radius <#stems> times in total length

expected_values["max_euclidean_distance"] = 375.7346033643161
expected_values["max_path_distance"] = 437.22941891149037

#expected_values["num_nodes"] = 1355
#expected_values["num_neurites"] = 1354

expected_values["total_volume"] = 478.72128143075264
expected_values["total_length"] = 1597.4876034705908
expected_values["num_stems"] = 1
#expected_values["num_bifurcations"] = 9
expected_values["num_tips"] = 10
expected_values["max_branch_order"] = 7

#expected_values["mean_fragmentation"] = 72.11111111111111
expected_values["contraction"] = 0.9108136972618417
expected_values["total_surface"] = 2814.8878834822463
expected_values["num_branches"] = 19
#expected_values["bifurcation_angle_remote"] = 53.00477565668728
#expected_values["bifurcation_angle_local"] = 75.51615372484065
#expected_values["mean_parent_daughter_ratio"] = 0.9546727368567294
expected_values["soma_surface"] = 505.68659921250304
expected_values["average_diameter"] = 0.5637629520295212
#expected_values["parent_daughter_ratio"] = 0.9546727368567297

names = []
for k in expected_values:
    names.append(k)
names.sort()

########################################################################

test_file = resource_filename(__name__, test_file)

def compare_value(table, name):
    global expected_values, pct_tolerance
    err = 0
    try:
        val = table[name]
        expected = expected_values[name]
    except:
        print("Field %s not found in table" % name)
        raise
    delta = abs(val - expected)
    if delta > 0.01 * pct_tolerance * abs(expected):
        print("Value %s out of tolerance" % name)
        print("    found %f" % val)
        print("    expected %f" % expected)
        err = 1
    return err

def test_features():
    global test_file
    morph = swc.read_swc(test_file)
    features = MorphologyFeatures(morph)
    #json.write("out.json", features.apical_dendrite)

    table = features.apical_dendrite
    errs = 0
    for name in names:
        errs += compare_value(table, name)
    
    num_tests = len(names)

    if errs > 0:
        raise Exception("Failed %d of %d tests" % (errs, num_tests))
    print("encountered %d errors in %d tests" % (errs, num_tests));


if __name__ == "__main__":
    test_features()

