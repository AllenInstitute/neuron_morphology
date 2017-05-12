from operator import add
from neuron_morphology.statistics import bits_statistics as bs

swc_statistics = [bs]


def morphology_statistics(morphology):

    stats = reduce(add, (s.statistics(morphology) for s in swc_statistics))

    return stats
