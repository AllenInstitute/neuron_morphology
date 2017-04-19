from operator import add
import bits_validation as bv
import marker_file as mf
import radius_validation as rv
import resample_validation as rev
import smooth_validation as sv
import type_validation as tv
import os

NEURON_MORPHOLOGY_VALIDATION_ROOT = os.path.dirname(os.path.abspath(__file__))

validators = [bv, mf, rv, rev, sv, tv]


def validate(morphology):

    errors = reduce(add, (v.validate(morphology) for v in validators))
    return errors

