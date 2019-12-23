from neuron_morphology.feature_extractor import FeatureExtractor
from neuron_morphology.feature_extractor.mark import (Marked,
    RequiresLayerAnnotations, Intrinsic, Geometric, AllNeuriteTypes,
    RequiresSoma)

from neuron_morphology.features import dimension

# Mark calculate_dimension_features()
calculate_dimension_features = Marked(set([Intrinsic, Geometric]))(
    dimension.calculate_dimension_features)


def default_feature_extractor():
    """Returns a feature extractor with default features"""

    fe = FeatureExtractor()

    fe.register_feature(calculate_dimension_features)


    return
