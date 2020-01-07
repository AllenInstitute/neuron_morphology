from neuron_morphology.constants import AXON, BASAL_DENDRITE, APICAL_DENDRITE
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.marked_feature import marked, specialize
from neuron_morphology.feature_extractor.mark import (
    RequiresLayerAnnotations, Intrinsic, Geometric, AllNeuriteTypes,
    RequiresSoma)
from neuron_morphology.feature_extractor.feature_specialization import \
    NEURITE_SPECIALIZATIONS

from neuron_morphology.features import dimension, intrinsic
from neuron_morphology.features.branching.outer_bifurcations import \
    num_outer_bifurcations
from neuron_morphology.features.size import (
    total_length, total_surface_area, total_volume, mean_diameter,
    mean_parent_daughter_ratio, max_euclidean_distance
)
from neuron_morphology.features.path import (
    max_path_distance, early_branch_path, mean_contraction
)


@marked(AllNeuriteTypes)
@marked(Geometric)
def dimension_features(data: Data):
    return dimension.calculate_dimension_features_for_all_types(data.morphology)


@marked(AllNeuriteTypes)
@marked(Intrinsic)
def intrinsic_features(data: Data):
    return intrinsic.calculate_intrinsic_features_for_all_types(data.morphology)


default_features = [
    dimension_features, 
    intrinsic_features,
    specialize(num_outer_bifurcations, NEURITE_SPECIALIZATIONS),
    specialize(total_length, NEURITE_SPECIALIZATIONS),
    specialize(total_surface_area, NEURITE_SPECIALIZATIONS),
    specialize(total_volume, NEURITE_SPECIALIZATIONS),
    specialize(mean_diameter, NEURITE_SPECIALIZATIONS),
    specialize(mean_parent_daughter_ratio, NEURITE_SPECIALIZATIONS),
    specialize(max_euclidean_distance, NEURITE_SPECIALIZATIONS),
    max_path_distance,
    early_branch_path,
    mean_contraction
]
