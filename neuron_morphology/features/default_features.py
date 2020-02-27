from neuron_morphology.constants import (
    AXON, BASAL_DENDRITE, APICAL_DENDRITE
)

# Feature Extractor, marks, and specializations
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.marked_feature import (
    marked, specialize, nested_specialize
)
from neuron_morphology.feature_extractor.mark import (
    RequiresLayerAnnotations, Intrinsic, Geometric, AllNeuriteTypes,
    RequiresSoma)
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS, NEURITE_COMPARISON_SPECIALIZATIONS,
    AxonSpec, ApicalDendriteSpec, BasalDendriteSpec, DendriteSpec,
    AxonCompareSpec, ApicalDendriteCompareSpec,
    BasalDendriteCompareSpec, DendriteCompareSpec,
)
from neuron_morphology.features.statistics.coordinates import COORD_TYPE_SPECIALIZATIONS
from neuron_morphology.features.layer.layer_histogram import (
    earth_movers_distance, normalized_depth_histogram)

# Features
from neuron_morphology.features.dimension import dimension
from neuron_morphology.features.intrinsic import (
    num_branches, num_tips, num_nodes, mean_fragmentation,
    max_branch_order
)
from neuron_morphology.features.branching.bifurcations import (
    num_outer_bifurcations, mean_bifurcation_angle_local, mean_bifurcation_angle_remote
)
from neuron_morphology.features.size import (
    total_length, total_surface_area, total_volume, mean_diameter,
    mean_parent_daughter_ratio, max_euclidean_distance
)
from neuron_morphology.features.path import (
    max_path_distance, early_branch_path, mean_contraction
)
from neuron_morphology.features.statistics.overlap import overlap
from neuron_morphology.features.statistics.moments import moments


default_features = [
    nested_specialize(
            dimension,
            [COORD_TYPE_SPECIALIZATIONS, NEURITE_SPECIALIZATIONS]),
    specialize(num_nodes, NEURITE_SPECIALIZATIONS),
    specialize(num_branches, NEURITE_SPECIALIZATIONS),
    specialize(num_tips, NEURITE_SPECIALIZATIONS),
    specialize(mean_fragmentation, NEURITE_SPECIALIZATIONS),
    specialize(max_branch_order, NEURITE_SPECIALIZATIONS),
    specialize(num_outer_bifurcations, NEURITE_SPECIALIZATIONS),
    specialize(mean_bifurcation_angle_local, NEURITE_SPECIALIZATIONS),
    specialize(mean_bifurcation_angle_remote, NEURITE_SPECIALIZATIONS),
    specialize(total_length, NEURITE_SPECIALIZATIONS),
    specialize(total_surface_area, NEURITE_SPECIALIZATIONS),
    specialize(total_volume, NEURITE_SPECIALIZATIONS),
    specialize(mean_diameter, NEURITE_SPECIALIZATIONS),
    specialize(mean_parent_daughter_ratio, NEURITE_SPECIALIZATIONS),
    specialize(max_euclidean_distance, NEURITE_SPECIALIZATIONS),
    max_path_distance,
    early_branch_path,
    mean_contraction,
    nested_specialize(
            overlap,
            [{AxonSpec, ApicalDendriteSpec, BasalDendriteSpec, DendriteSpec},
             {AxonCompareSpec, ApicalDendriteCompareSpec,
              BasalDendriteCompareSpec,
              DendriteCompareSpec}]),
    nested_specialize(
            moments,
            [COORD_TYPE_SPECIALIZATIONS, NEURITE_SPECIALIZATIONS]),
    specialize(normalized_depth_histogram, NEURITE_SPECIALIZATIONS),
    nested_specialize(
        earth_movers_distance, 
        [
            {AxonSpec, ApicalDendriteSpec, BasalDendriteSpec, DendriteSpec},
            {
                AxonCompareSpec, ApicalDendriteCompareSpec,
                BasalDendriteCompareSpec,
                DendriteCompareSpec
            },
        ]
    )

]
