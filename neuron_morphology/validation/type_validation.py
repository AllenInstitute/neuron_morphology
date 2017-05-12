# Copyright 2015-2017 Allen Institute for Brain Science
# This file is part of Allen SDK.
#
# Allen SDK is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Allen SDK is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Allen SDK.  If not, see <http://www.gnu.org/licenses/>.
# Author: Nika Keller

from errors import NodeValidationError as ve
from neuron_morphology.constants import *

valid_types = {SOMA, AXON, BASAL_DENDRITE, APICAL_DENDRITE}


def validate_count_node_parent(morphology, node_type, parent_type, expected_count):

    """ This function validates the number of nodes that have a specific type of parent """

    tree = morphology.tree(0)
    matched_node_numbers = []
    errors = []

    for node in tree:
        if node.t == node_type and morphology.parent_of(node).t is parent_type:
            matched_node_numbers.append(node.original_n)

    if len(matched_node_numbers) > expected_count:
        for node_number in matched_node_numbers:
            errors.append(ve("Nodes of type %s can only have %s parent of type %s" % (node_type, expected_count
                                                                                      , parent_type), node_number
                                                                                                    , "Medium"))

    return errors


def validate_number_of_soma_nodes(morphology):
    """ This function validates the number of type 1 nodes """

    errors = []
    matched_node_numbers = []

    for tree in range(0, morphology.num_trees):
        for node in morphology.tree(tree):
            if node.t == SOMA:
                matched_node_numbers.append(node.original_n)

    if len(matched_node_numbers) != 1:
        for node_number in matched_node_numbers:
            errors.append(ve("The morphology needs to have one soma node", node_number, "High"))

    return errors


def validate_expected_types(node):

    """ This function validates the expected types of the nodes """

    errors = []

    if node.t not in valid_types:
        errors.append(ve("Node type needs to be one of these values: %s" % valid_types, node.original_n, "Medium"))

    return errors


def validate_node_parent(morphology, node):

    """ This function validates the type of parent node for a specific type of child node """

    errors = []
    valid_soma_parents = {None}
    valid_axon_parents = {SOMA, AXON, BASAL_DENDRITE, None}
    valid_basal_dendrite_parents = {SOMA, BASAL_DENDRITE}
    valid_apical_dendrite_parents = {SOMA, APICAL_DENDRITE}

    if node.t == SOMA:
        if morphology.parent_of(node):
            errors.append(ve("Type 1 can only have a parent of the following types: %s" % valid_soma_parents
                             , node.original_n, "Medium"))
    if node.t == AXON:
        if morphology.parent_of(node):
            if morphology.parent_of(node).t not in valid_axon_parents:
                errors.append(ve("Type 2 can only have a parent of the following types: %s" % valid_axon_parents
                                 , node.original_n, "Medium"))
    if node.t == BASAL_DENDRITE:
        if morphology.parent_of(node).t not in valid_basal_dendrite_parents:
            errors.append(ve("Type 3 can only have a parent of the following types: %s" % valid_basal_dendrite_parents
                             , node.original_n, "Medium"))
    if node.t == APICAL_DENDRITE:
        parent = morphology.parent_of(node)
        if parent and parent.t not in valid_apical_dendrite_parents:
            errors.append(ve("Type 4 can only have a parent of the following types: %s" % valid_apical_dendrite_parents
                             , node.original_n, "Medium"))

    return errors


def validate_immediate_children_of_soma_cannot_branch(morphology, node):

    """ This function validates that immediate children of soma cannot branch """

    errors = []

    if morphology.parent_of(node):
        if morphology.parent_of(node).t == SOMA:
            if len(morphology.children_of(node)) > 1:
                errors.append(ve("Immediate children of soma cannnot branch", node.original_n, "High"))

    return errors


def validate(morphology):

    errors = []

    for tree in range(0, morphology.num_trees):
        for tree_node in morphology.tree(tree):
            errors += validate_expected_types(tree_node)

            errors += validate_node_parent(morphology, tree_node)

            errors += validate_immediate_children_of_soma_cannot_branch(morphology, tree_node)

    """ nodes that are type 4 can only have one parent parent of type 1 """
    errors += validate_count_node_parent(morphology, APICAL_DENDRITE, SOMA, 1)

    """ There can only be one node of type 1 """
    errors += validate_number_of_soma_nodes(morphology)

    return errors
