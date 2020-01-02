from functools import partial

from neuron_morphology.feature_extractor.marked_feature import (
    MarkedFeature, marked
)
from neuron_morphology.feature_extractor.mark import (
    RequiresRoot, 
    BifurcationFeatures, 
    RequiresApical,
    RequiresBasal,
    RequiresAxon
)
from neuron_morphology.constants import (
    AXON, BASAL_DENDRITE, APICAL_DENDRITE
)


__all__ = [
    "num_outer_bifurcations",
    "apical_num_outer_bifurcations",
    "basal_num_outer_bifurcations",
    "axon_num_outer_bifurcations"
]


def calculate_outer_bifs(morphology, soma, node_types):

    """
        Counts the number of bifurcation points beyond the a sphere
        with 1/2 the radius from the soma to the most distant point
        in the morphology, with that sphere centered at the soma.

        Parameters
        ----------

        morphology: Morphology object

        soma:

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)
        Type to restrict search to

        Returns
        -------

        int: the number of bifurcations

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
def num_outer_bifurcations(data, node_types=None):
    return count_outer_bifs(
        data.morphology, 
        data.morphology.get_root(), 
        node_types
    )


@marked(BifurcationFeatures)
@marked(RequiresRoot)
@marked(RequiresApical)
def apical_num_outer_bifurcations(data):
    return num_outer_bifuractions(data, [APICAL_DENDRITE])


@marked(BifurcationFeatures)
@marked(RequiresRoot)
@marked(RequiresBasal)
def basal_num_outer_bifurcations(data):
    return num_outer_bifuractions(data, [BASAL_DENDRITE])


@marked(BifurcationFeatures)
@marked(RequiresRoot)
@marked(RequiresAxon)
def axon_num_outer_bifurcations(data):
    return num_outer_bifuractions(data, [AXON])
