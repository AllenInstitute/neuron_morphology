from neuron_morphology.constants import AXON, BASAL_DENDRITE, APICAL_DENDRITE


def calculate_dimension_features_for_all_types(morphology):
    """Calculate dimension features for all node types."""
    features = {}
    features['all_neurites'] = calculate_dimension_features(morphology)
    features['axon'] = calculate_dimension_features(
        morphology, node_types=[AXON])
    features['basal_dendrite'] = calculate_dimension_features(
        morphology, node_types=[BASAL_DENDRITE])
    features['apical_dendrite'] = calculate_dimension_features(
        morphology, node_types=[APICAL_DENDRITE])

    return features


def calculate_dimension_features(morphology, node_types=None):
    """Calculate dimension features for a morphology."""
    features = {}
    dims = morphology.get_dimensions(node_types)
    if dims is not None:
        low = dims[1]
        high = dims[2]
        features["width"] = dims[0][0]
        features["height"] = dims[0][1]
        features["depth"] = dims[0][2]
        features["min_x"] = low[0]
        features["min_y"] = low[1]
        features["min_z"] = low[2]
        features["max_x"] = high[0]
        features["max_y"] = high[1]
        features["max_z"] = high[2]

    else:
        features["width"] = float('nan')
        features["height"] = float('nan')
        features["depth"] = float('nan')
        features["min_x"] = float('nan')
        features["min_y"] = float('nan')
        features["min_z"] = float('nan')
        features["max_x"] = float('nan')
        features["max_y"] = float('nan')
        features["max_z"] = float('nan')

    return features
