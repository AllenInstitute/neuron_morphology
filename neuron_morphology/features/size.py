from typing import Optional, List, Union, Dict, Any
from statistics import mean
from collections import defaultdict
from functools import partial

from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import SOMA
from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    Geometric, RequiresRadii, RequiresRoot)
from neuron_morphology.feature_extractor.data import (
    MorphologyLike, get_morphology)

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
        if first_node_in_compartment['type'] is SOMA \
            and not morphology.parent_of(first_node_in_compartment):
            continue
        total += morphology.get_compartment_length(compartment)

    return total


@marked(RequiresRadii)
@marked(Geometric)
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
    data : The reconstruction whose surface area will be computed
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


@marked(RequiresRadii)
@marked(Geometric)
def total_volume(
    data: MorphologyLike, 
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculates the sum of volumes across all comparments (linked pairs of 
    nodes) in a reconstruction. This approximates the total volume of the 
    reconstruction. See Morphology.get_compartment_volume for details.

    Parameters
    ----------
    data : The reconstruction whose volume will be computed
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


@marked(RequiresRadii)
def mean_diameter(
    data: MorphologyLike, 
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculates the mean diameter of all nodes
    
    Parameters
    ----------
    morphology : The reconstruction whose mean diameter
    node_types : restrict the calculation to compartments involving these node 
        types

    Returns
    -------
    The average diameter across selected nodes

    """

    morphology = get_morphology(data)

    return 2 * mean(
        node["radius"] for node in morphology.get_node_by_types(node_types)
    )



def parent_daughter_ratio_visitor(
    node: Dict[str, Any], 
    morphology: Morphology, 
    counters: Dict[str, Union[int, float]],
    node_types: Optional[List[int]] = None
):
    """ Calculates for a single node the ratio of the node's parent's radius to 
    the node's radius. Stores these values in a provided dictionary.

    Parameters
    ----------
    node : The node under consideration
    morphology : The reconstruction to which this node belongs
    counters : a dictionary used for storing running ratio totals and counts.
    node_types : skip nodes not of one of these types

    Notes
    -----
    see mean_parent_daughter_ratio for usage

    """

    parent = morphology.parent_of(node)
    
    if parent is None:
        return

    if node_types is not None:
        if node["type"] not in node_types or parent["type"] not in node_types:
            return

    counters["ratio_sum"] += parent["radius"] / node["radius"]
    counters["ratio_count"] += 1
    

@marked(RequiresRadii)
def mean_parent_daughter_ratio(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> float:
    """ Calculate the average ratio of parent radii to child radii across a 
    reconstruction.

    Parameters
    ----------
    data : The reconstruction whose mean parent daugther ratio will be computed
    node_types : restrict the calculation to compartments involving these node 
        types

    Notes
    -----
    Note that this function differs from the L-measure parent daughter ratio, 
    which calculates the ratio of the child node size to the parent. Note also 
    that both the parent and child must be in node_types in order for a
    compartment to be included in the calculation

    """

    morphology = get_morphology(data)
    roots = morphology.get_roots()
    
    counters: Dict[str, int] = defaultdict(lambda *a, **k: 0)
    visitor = partial(
        parent_daughter_ratio_visitor, 
        morphology=morphology, 
        counters=counters,
        node_types=node_types
    )
    
    for root in roots:
        morphology.breadth_first_traversal(
            visitor, 
            start_id=morphology.node_id_cb(root)
        )

    return counters["ratio_sum"] / counters["ratio_count"]


@marked(RequiresRoot)
@marked(Geometric)
def max_euclidean_distance(
    data: MorphologyLike,
    node_types: Optional[List[int]] = None
) -> float:
    """Calculate the furthest distance, in 3-space, of a compartment's end from 
    the soma. This is equivalent to the distance to the furthest SWC node.

    Parameters
    ----------
    data: The reconstruction whose max euclidean distance will be 
        calculated
    node_types: restrict consideration to these types

    Returns
    -------
    The distance between the soma and the farthest-from-soma node in this 
    morphology.

    """

    morphology = get_morphology(data)
    soma = morphology.get_root()

    return max(
        morphology.euclidean_distance(soma, node)
        for node in morphology.get_node_by_types(node_types)
    )
