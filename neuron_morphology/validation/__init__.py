from operator import add
import bits_validation as bv
import marker_file as mf
import radius_validation as rv
import resample_validation as rev
import smooth_validation as sv
import type_validation as tv


def validate(morphology):
    #validators = [bv, mf, rv, rev, sv, tv]
    validators = [tv]
    errors = reduce(add, (v.validate(morphology) for v in validators))
    return errors

