from neuron_morphology.features.common import calculate_max_euclidean_distance
from neuron_morphology.features.dimension import calculate_dimension_features
from neuron_morphology.features.compartment_moments import calculate_compartment_moment_features


def calculate_axon_cloud_features(morphology, node_types):

    # calculate axon cloud features -- ie, the subset of features of
    #   that can be calculated on an entire disconnected axon
    # ** out-of-order calculation **
    # max distance must be measured with soma present. for cloud, this
    #   must be calculated before non-soma branches are pruned

    features = {}
    ax_dist = calculate_max_euclidean_distance(morphology, node_types)
    calculate_compartment_moment_features(morphology, node_types)
    calculate_dimension_features(morphology, node_types)
    features["max_euclidean_distance"] = ax_dist

    return features
