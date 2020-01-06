from typing import Optional, List, Union

from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.constants import SOMA
from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import Geometric


MorphologyLike = Union[Data, Morphology]


def get_morphology(data: MorphologyLike):
    if isinstance(data, Morphology):
        return data
    return data.morphology


@marked(Geometric)
def total_length(
    data: MorphologyLike, 
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


def total_surface_area(
    data: MorphologyLike, 
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculates the sum of lateral surface areas across all comparments 
    (linked pairs of nodes) in a reconstruction. This approximates the total 
    surface area of the reconstruction. See 
    Morphology.get_compartment_surface_area for details.

    Parameters
    ----------
    morphology : The reconstruction whose surface area will be computed
    node_types : restrict the calculation to compartments involving these node 
        types

    Returns
    -------
    The sum of compartment lateral surface areas across this reconstruction

    """

    morphology: Morphology = get_morphology(data)
    nodes = morphology.get_node_by_types(node_types)
    compartments = morphology.get_compartments(nodes, node_types)

    return sum(map(morphology.get_compartment_surface_area, compartments))


def total_volume(
    data: MorphologyLike, 
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculates the sum of volumes across all comparments (linked pairs of 
    nodes) in a reconstruction. This approximates the total volume of the 
    reconstruction. See Morphology.get_compartment_volume for details.

    Parameters
    ----------
    morphology : The reconstruction whose volume will be computed
    node_types : restrict the calculation to compartments involving these node 
        types

    Returns
    -------
    The sum of compartment volumes across this reconstruction

    """
    
    morphology = get_morphology(data)
    nodes = morphology.get_node_by_types(node_types)
    compartments = morphology.get_compartments(nodes, node_types)

    return sum(map(morphology.get_compartment_volume, compartments))
