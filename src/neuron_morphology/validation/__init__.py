from operator import add
from . import bits_validation as bv
from . import marker_validation as mv
from . import radius_validation as rv
from . import resample_validation as rev
from . import type_validation as tv
from . import structure_validation as stv
from functools import reduce


swc_validators = [bv, rv, rev, tv, stv]
marker_validators = [mv]


def validate_morphology(morphology):

    result = reduce(add, (sv.validate(morphology) for sv in swc_validators))

    return result


def validate_marker(marker, morphology):

    result = reduce(add, (m.validate(marker, morphology) for m in marker_validators))

    return result
