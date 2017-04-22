from operator import add
import bits_validation as bv
import marker_file as mf
import radius_validation as rv
import resample_validation as rev
import type_validation as tv

validators = [bv, mf, rv, rev, tv]


def validate(morphology):

    errors = reduce(add, (v.validate(morphology) for v in validators))

    return errors

