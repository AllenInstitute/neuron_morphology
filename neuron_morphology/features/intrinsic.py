from neuron_morphology.constants import AXON, BASAL_DENDRITE, APICAL_DENDRITE

# TODO: clean up core_features and pull these functions out to this file
from neuron_morphology.features.core_features import (
    calculate_number_of_branches,
    calculate_max_branch_order,
    calculate_mean_fragmentation,
    calculate_number_of_tips)


def calculate_intrinsic_features_for_all_types(morphology):
    """Calculate intrinsic features for all node types."""
    features = {}
    features['all_neurites'] = calculate_intrinsic_features(morphology)
    features['axon'] = calculate_intrinsic_features(
        morphology, node_types=[AXON])
    features['basal_dendrite'] = calculate_intrinsic_features(
        morphology, node_types=[BASAL_DENDRITE])
    features['apical_dendrite'] = calculate_intrinsic_features(
        morphology, node_types=[APICAL_DENDRITE])

    return features


def calculate_intrinsic_features(morphology, node_types=None):
    features = {}

    features['num_branches'] = calculate_number_of_branches(
            morphology, node_types=node_types)
    features['max_branch_order'] = calculate_max_branch_order(
        morphology, node_types=node_types)
    features['mean_fragmentation'] = calculate_mean_fragmentation(
        morphology, node_types=node_types)
    features['num_tips'] = calculate_number_of_tips(
        morphology, node_types=node_types)
    features['num_nodes'] = len(morphology.get_node_by_types(node_types))

    return features
