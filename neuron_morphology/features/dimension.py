def calculate_dimensions(morphology, node_types):

    """
        Measures overall size on each dimension: width(x), height(z) and depth(z).
        Soma nodes are not included in this measurement.

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        3-element array: [width, height, depth]

    """

    return morphology.get_dimensions(node_types)


def calculate_dimension_features(morphology, node_types):
    features = {}
    dims = calculate_dimensions(morphology, node_types)
    if dims is not None:
        low = dims[1]
        high = dims[2]
        features["width"] = dims[0][0]
        features["height"] = dims[0][1]
        features["depth"] = dims[0][2]
        features["low_x"] = low[0]
        features["low_y"] = low[1]
        features["low_z"] = low[2]
        features["high_x"] = high[0]
        features["high_y"] = high[1]
        features["high_z"] = high[2]

    else:
        features["width"] = float('nan')
        features["height"] = float('nan')
        features["depth"] = float('nan')
        features["low_x"] = float('nan')
        features["low_y"] = float('nan')
        features["low_z"] = float('nan')
        features["high_x"] = float('nan')
        features["high_y"] = float('nan')
        features["high_z"] = float('nan')

    return features
