from typing import Optional, List
from enum import Enum

from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import (
    Geometric,
    BifurcationFeatures,
    CompartmentFeatures,
    TipFeatures)


class CoordinateType(Enum):
    NODE = 0
    COMPARTMENT = 1
    BIFURCATION = 2
    TIP = 3

    def get_coordinates(self, morphology,
                        node_types: Optional[List[int]] = None):
        fn = {CoordinateType.NODE: get_node_coordinates,
              CoordinateType.BIFURCATION: get_bifurcation_coordinates,
              CoordinateType.COMPARTMENT: get_compartment_coordinates,
              CoordinateType.TIP: get_tip_coordinates}.get(self)
        return fn(morphology, node_types=node_types)


@marked(Geometric)
@marked(CompartmentFeatures)
def get_compartment_coordinates(morphology,
                                node_types: Optional[List[int]] = None):
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
def get_bifurcation_coordinates(morphology,
                                node_types: Optional[List[int]] = None):
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
@marked(TipFeatures)
def get_tip_coordinates(morphology,
                        node_types: Optional[List[int]] = None):
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


@marked(Geometric)
def get_node_coordinates(morphology,
                         node_types: Optional[List[int]] = None):
    """
        Return the coordinates of each node in the morphology

        Parameters
        ----------

        morphology: Morphology object

        node_types: list (AXON, BASAL_DENDRITE, APICAL_DENDRITE)

        Returns
        -------

        list: list of coordinates [x, y, z]


    """
    nodes = morphology.get_node_by_types(node_types=node_types)
    return [[node['x'], node['y'], node['z']] for node in nodes]


@marked(Geometric)
def get_coordinates(
        morphology: Morphology,
        coordinate_type: CoordinateType = CoordinateType.NODE,
        node_types: Optional[List[int]] = None):

    return coordinate_type.get_coordinates(morphology, node_types=node_types)
