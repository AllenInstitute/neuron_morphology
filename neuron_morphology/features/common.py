import numpy as np
import scipy.stats

from allensdk.deprecated import deprecated


def calculate_skewness(values_x, values_y, values_z):

    #########################
    # calculate third moment (skewness)
    # from wikipedia:
    #   skew = E[((X-mean)/stdev)^3]
    # where E[x] is the mean of all values x
    # NOTE: scipy eliminates ability to weigh compartments by length,
    #   so result will be biased by segmentation strategy

    skew = np.zeros(3)
    skew[0] = scipy.stats.skew(np.asarray(values_x))
    skew[1] = scipy.stats.skew(np.asarray(values_y))
    skew[2] = scipy.stats.skew(np.asarray(values_z))
    return skew


def calculate_kurtosis(values_x, values_y, values_z):

    kurtosis = np.zeros(3)
    kurtosis[0] = scipy.stats.kurtosis(values_x)
    kurtosis[1] = scipy.stats.kurtosis(values_y)
    kurtosis[2] = scipy.stats.kurtosis(values_z)
    return kurtosis


@deprecated("use size.max_euclidean_distance instead")
def calculate_max_euclidean_distance(morphology, node_types):

    """
        Calculate the furthest distance, in 3-space, of a
        compartment's end from the soma.
        This is equivalent to the distance to the furthest SWC node.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        Scalar value

    """

    soma = morphology.get_root()
    nodes = morphology.get_node_by_types(node_types)

    distances = []
    for node in nodes:
        distances.append(morphology.euclidean_distance(soma, node))

    return max(distances)
