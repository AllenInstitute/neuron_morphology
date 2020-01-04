from neuron_morphology.feature_extractor.marked_feature import marked

from neuron_morphology.feature_extractor.mark import (
    Geometric,
    BifurcationFeatures,
    CompartmentFeatures)


@marked(Geometric)
@marked(CompartmentFeatures)
def get_compartment_coordinates(morphology, node_types=None):
    """
        Return the coordinates of the midpoint of each compartment
        in the morphology

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)

        Returns
        -------

        list: list of coordinates [x, y, z]


    """
    comps = morphology.get_compartments()
    return [morphology.get_compartment_midpoint(comp) for comp in comps]


@marked(Geometric)
@marked(BifurcationFeatures)
def get_bifurcation_coordinates(morphology, node_types=None):
    """
        Return the coordinates of each bifurcation in the morphology

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)

        Returns
        -------

        list: list of coordinates [x, y, z]


    """
    bifs = morphology.get_branching_nodes(node_types=node_types)
    return [[bif['x'], bif['y'], bif['z']] for bif in bifs]


@marked(Geometric)
def get_tip_coordinates(morphology, node_types=None):
    """
        Return the coordinates of each tip in the morphology

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)

        Returns
        -------

        list: list of coordinates [x, y, z]


    """
    tips = morphology.get_leaf_nodes(node_types=node_types)
    return [[tip['x'], tip['y'], tip['z']] for tip in tips]


tree_coordinate_features = [get_compartment_coordinates,
                            get_bifurcation_coordinates,
                            get_tip_coordinates]
