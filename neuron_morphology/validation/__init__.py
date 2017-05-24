from operator import add
import bits_validation as bv
import marker_validation as mv
import radius_validation as rv
import resample_validation as rev
import type_validation as tv

swc_validators = [bv, rv, rev, tv]
marker_validators = [mv]


def validate_morphology(morphology):

    result = reduce(add, (sv.validate(morphology) for sv in swc_validators))

    return result


def validate_marker(marker, morphology):

    result = reduce(add, (m.validate(marker, morphology) for m in marker_validators))

    return result
