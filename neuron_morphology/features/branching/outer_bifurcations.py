from typing import Optional, List, Dict

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    RequiresRoot, 
    BifurcationFeatures,
)
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.morphology import Morphology


__all__ = [
    "num_outer_bifurcations",
    "calculate_outer_bifs"
]


def calculate_outer_bifs(
    morphology: Morphology, 
    soma: Dict, 
    node_types: Optional[List[int]]
) -> int:

    """
        Counts the number of bifurcation points beyond the a sphere
        with 1/2 the radius from the soma to the most distant point
        in the morphology, with that sphere centered at the soma.

        Parameters
        ----------
        morphology: Describes the structure of a neuron
        soma: Must have keys "x", "y", and "z", describing the position of this 
            morphology's soma in 
        node_types: Restrict included nodes to these types. See 
            neuron_morphology.constants for avaiable node types. 

        Returns
        -------
        the number of bifurcations 

    """

    nodes = morphology.get_node_by_types(node_types)
    far = 0
    for node in nodes:
        dist = morphology.euclidean_distance(soma, node)
        if dist > far:
            far = dist

    count = 0
    rad = far / 2.0
    for node in nodes:
        if len(morphology.children_of(node)) > 1:
            dist = morphology.euclidean_distance(soma, node)
            if dist > rad:
                count += 1
    return count


@marked(BifurcationFeatures)
@marked(RequiresRoot)
def num_outer_bifurcations(
    data: Data, 
    node_types: Optional[List[int]]= None
) -> int:
    """ Feature Extractor interface to calculate_outer_bifurcations. Returns the 
    number of bifurcations (branch points), excluding those too close to the 
    root (threshold is 1/2 the max distance from the root to any node).

    Parameters
    ----------
    data : Holds a morphology object. No additional data is required
    node_types : Restrict included nodes to these types. See 
        neuron_morphology.constants for avaiable node types. 

    """

    return calculate_outer_bifs(
        data.morphology, 
        data.morphology.get_root(), 
        node_types
    )
