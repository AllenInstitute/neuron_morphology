from typing import NamedTuple, Optional, Dict, Sequence

import numpy as np
import pandas as pd

from neuron_morphology.features.layer.reference_layer_depths import \
    ReferenceLayerDepths
from neuron_morphology.features.layer.layered_point_depths import \
    LayeredPointDepths
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.mark import (
    RequiresReferenceLayerDepths, 
    RequiresLayeredPointDepths, 
    RequiresRegularNodeSpacing
)
from neuron_morphology.feature_extractor.marked_feature import marked


class LayerHistogram(NamedTuple):
    counts: np.ndarray
    bin_edges: np.ndarray


@marked(RequiresRegularNodeSpacing)
@marked(RequiresLayeredPointDepths)
@marked(RequiresReferenceLayerDepths)
def normalized_depth_histogram(
    data: Data, 
    node_types: Optional[Sequence[int]] = None,
    bin_size=5.0
) -> Dict[str, LayerHistogram]:
    """ A shim for specializing normalized_depth_histograms across node types
    """

    return normalized_depth_histograms(
        data=data, node_types=node_types, bin_size=bin_size)

def normalized_depth_histograms_across_layers(
    data: Data, 
    point_types: Optional[Sequence[int]] = None,
    bin_size=5.0
) -> Dict[str, LayerHistogram]:
    """ Calculates for each cortical layer a histogram of node depths within 
    that layer.

    Parameters
    ----------
    data : Must have the following attributes:
        reference_layer_depths : A dictionary mapping layer names (str) to 
            ReferenceLayerDepths objects describing the average pia and white-
            matter side depths of this each layer.
        layered_point_depths : A LayeredPointDepths defining for 

    """

    depths = data.layered_point_depths.df # type: ignore[attr-defined]
    if node_types is not None and "point_type" in depths:
        depths = depths.loc[:, depths["point_type"].isin(set(point_types))]

    output = {}

    for layer_name, group in depths.groupby("layer_name"):
        reference_layer_depths = data.reference_layer_depths.get( # type: ignore[attr-defined]
            layer_name, None)
        if reference_layer_depths is None:
            raise ValueError(
                "unable to calculate layer depth histogram for layer "
                f"{layer_name} - no reference depths provided"
            )

        group_df = pd.DataFrame(group)
        output[layer_name] = normalized_depth_histogram_within_layer(
            point_depths=group_df["depth"],
            local_layer_pia_side_depths=group_df["local_layer_pia_side_depth"],
            local_layer_wm_side_depths=group_df["local_layer_wm_side_depth"],
            reference_layer_depths=reference_layer_depths,
            bin_size=bin_size
        )

    return output


def normalized_depth_histogram_within_layer(
    point_depths: np.ndarray,
    local_layer_pia_side_depths: np.ndarray,
    local_layer_wm_side_depths: np.ndarray,
    reference_layer_depths: ReferenceLayerDepths,
    bin_size: float
) -> np.ndarray:
    """ Calculates a histogram of node depths within a single (cortical) layer. 
    Uses reference information about layer boundaries to normalize these 
    depths for cross-reconstruction comparison.

    Parameters
    ----------
    depths : Each item corresponds to a point of interest (such as a node 
        in a morphological reconstruction). Values are the depths of these 
        points of interest from the pia surface.
    local_layer_pia_side_depths : Each item corresponds to a point of interest.
        Values are the depth of the intersection point between a path of 
        steepest descent from the pia surface to the point of interest and the 
        upper surface of the layer.
    local_layer_wm_side_depths : Each item corresponds to a point of interest. 
        Values are the depth of the intersection point between the layer's 
        lower boundary and the path described above.
    reference_layer_depths : Used to provide normalized depths suitable 
        for comparison across reconstructions. Should provide a generic 
        equivalent of local layer depths for a population or reference space.
    bin_size : The width of each bin, in terms of depths from pia in the 
        reference space. Provide only one of bin_edges or bin_size.
    
    Returns
    -------
    A numpy array listing for each depth bin the number of nodes falling within 
        that bin.

    Notes
    -----
    This function relies on the notion of a steepest descent path through 
    cortex, but is agnostic to the method used to obtain such a path and to 
    features of the path (e.g. whether it is allowed to curve). Rather the 
    caller must ensure that all depths have been calculated according to a 
    consistent scheme. 

    """

    bin_edges = np.arange(
        reference_layer_depths.pia_side,
        reference_layer_depths.wm_side,
        bin_size
    )
    if reference_layer_depths.wm_side - bin_edges[-1] > 0.5 * bin_size:
        bin_edges = np.append(bin_edges, [reference_layer_depths.wm_side])
    else:
        bin_edges[-1] = reference_layer_depths.wm_side

    if reference_layer_depths.scale:
        local_layer_thicknesses = \
            local_layer_wm_side_depths - local_layer_pia_side_depths
        scale = reference_layer_depths.thickness / local_layer_thicknesses
    else:
        scale = 1.0

    normalized_depths = (point_depths - local_layer_pia_side_depths) * scale
    normalized_depths = normalized_depth_histogram + local_layer_pia_side_depths
    normalized_depths = normalized_depths[np.isfinite(normalized_depths)]

    counts, bin_edges = np.histogram(normalized_depths, bins=bin_edges)
    return LayerHistogram(counts=counts, bin_edges=bin_edges)


