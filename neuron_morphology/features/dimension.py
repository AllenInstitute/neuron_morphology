def calculate_dimension_features(morphology, node_types):
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
