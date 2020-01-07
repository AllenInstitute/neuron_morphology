from typing import Optional, List

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.statistics.coordinates import COORD_TYPE

from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.mark import Intrinsic

# TODO: clean up core_features and pull these functions out to this file
from neuron_morphology.features.core_features import (
    calculate_number_of_branches,
    calculate_max_branch_order,
    calculate_mean_fragmentation,
    calculate_number_of_tips)


@marked(Intrinsic)
def num_branches(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate number of branches

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    num_branches = calculate_number_of_branches(data.morphology,
                                                node_types=node_types)
    return num_branches


@marked(Intrinsic)
def num_tips(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate number of tips

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    # Alternative method:
    # num_tips = len(COORD_TYPE.TIP.get_coordinates(data.morphology,
    #                                               node_types=node_types))
    num_tips = calculate_number_of_tips(data.morphology, node_types=node_types)
    return num_tips


@marked(Intrinsic)
def num_nodes(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate number of nodes of a given type

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    num_nodes = len(data.morphology.get_node_by_types(node_types))
    return num_nodes


@marked(Intrinsic)
def mean_fragmentation(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate mean fragmentation

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    mean_fragmentation = calculate_mean_fragmentation(data.morphology,
                                                      node_types=node_types)
    return mean_fragmentation


@marked(Intrinsic)
def max_branch_order(
        data: Data,
        node_types: Optional[List] = None,
        ):
    """
        Calculate mean fragmentation

        Parameters
        ----------

        data: Data Object containing a morphology

        node_types: a list of node types (see neuron_morphology constants)

    """
    max_branch_order = calculate_max_branch_order(data.morphology,
                                                  node_types=node_types)
    return max_branch_order
