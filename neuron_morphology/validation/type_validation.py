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

from errors import ValidationError as ve

valid_types = {1, 2, 3, 4}


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
                                                                                    , parent_type), node_number, False))

    return errors


def validate_number_of_type1_nodes(morphology):
    """ This function validates the number of type 1 nodes """

    errors = []
    matched_node_numbers = []

    for tree in range(0, morphology.num_trees):
        for node in morphology.tree(tree):
            if node.t == 1:
                matched_node_numbers.append(node.original_n)

    if len(matched_node_numbers) > 1:
        for node_number in matched_node_numbers:
            errors.append(ve("There can only be one node of type 1", node_number, False))

    return errors


def validate_expected_types(node):

    """ This function validates the expected types of the nodes """

    errors = []

    if node.t not in valid_types:
        errors.append(ve("Node type needs to be one of these values: %s" % valid_types, node.original_n, False))

    return errors


def validate_node_parent(morphology, node):

    """ This function validates the type of parent node for a specific type of child node """

    errors = []
    valid_type_one_parents = {-1}
    valid_type_two_parents = {1, 2, 3, -1}
    valid_type_three_parents = {1, 3}
    valid_type_four_parents = {1, 4}

    if node.t == 1:
        if morphology.parent_of(node):
            errors.append(ve("Type 1 can only have a parent of the following types: %s" % valid_type_one_parents
                             , node.original_n, False))
    if node.t == 2:
        if morphology.parent_of(node).t not in valid_type_two_parents:
            errors.append(ve("Type 2 can only have a parent of the following types: %s" % valid_type_two_parents
                             , node.original_n, False))
    if node.t == 3:
        if morphology.parent_of(node).t not in valid_type_three_parents:
            errors.append(ve("Type 3 can only have a parent of the following types: %s" % valid_type_three_parents
                             , node.original_n, False))
    if node.t == 4:
        parent = morphology.parent_of(node)
        if parent and parent.t not in valid_type_four_parents:
            errors.append(ve("Type 4 can only have a parent of the following types: %s" % valid_type_four_parents
                             , node.original_n, False))

    return errors


def validate(morphology):

    errors = []
    tree = morphology.tree(0)
    for tree_node in tree:
        errors += validate_expected_types(morphology.node(tree_node))

        errors += validate_node_parent(morphology, morphology.node(tree_node))

    """ nodes that are type 4 can only have one parent parent of type 1 """
    errors += validate_count_node_parent(morphology, 4, 1, 1)

    """ There can only be one node of type 1 """
    errors += validate_number_of_type1_nodes(morphology)

    return errors
