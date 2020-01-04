from typing import Optional, List, Union

from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.constants import SOMA
from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import Geometric


def get_morphology(data: Union[Data, Morphology]):
    if isinstance(data, Morphology):
        return data
    return data.morphology


@marked(Geometric)
def total_length(
    data: Union[Data, Morphology], 
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculate the total length across all compartments in a reconstruction

    Parameters
    ----------
    data : the input reconstruction
    node_types : if provided, restrict the calculation to compartments 
        involving these types

    Returns
    -------
    The sum of segment lengths across all segments in the reconstruction

    Notes
    -----
    Excludes compartments where the parent is:
        1. the soma
        2. a root of the reconstruction
    The logic here is that the soma root is likely to substantially overlap any 
    of its compartments, while non-root soma nodes will be closer to the soma 
    surface.

    """

    morphology = get_morphology(data)

    nodes = morphology.get_node_by_types(node_types)
    compartment_list = morphology.get_compartments(nodes, node_types)

    total = 0.0
    for compartment in compartment_list:
        first_node_in_compartment = compartment[0]
        if first_node_in_compartment['type'] is SOMA and not morphology.parent_of(first_node_in_compartment):
            continue
        total += morphology.get_compartment_length(compartment)

    return total
