from result import NodeValidationError as ve
from allensdk.neuron_morphology.constants import *

valid_types = {SOMA, AXON, BASAL_DENDRITE, APICAL_DENDRITE}


def validate_count_node_parent(morphology, node_type, parent_type, expected_count):

    """ This function validates the number of nodes that have a specific type of parent """

    matched_node_numbers = []
    result = []

    for node in morphology.nodes():
        if morphology.parent_of(node):
            if node['type'] is node_type and morphology.parent_of(node)['type'] is parent_type:
                matched_node_numbers.append(node['id'])

    if len(matched_node_numbers) > expected_count:
        for node_number in matched_node_numbers:
            result.append(ve("Nodes of type %s can only have %s parent of type %s" % (node_type, expected_count
                                                                                      , parent_type), node_number
                                                                                                    , "Warning"))

    return result


def validate_number_of_soma_nodes(morphology):
    """ This function validates the number of type 1 nodes """

    result = []
    matched_node_numbers = []

    for node in morphology.nodes():
        if node['type'] == SOMA:
            matched_node_numbers.append(node['id'])

    if len(matched_node_numbers) != 1:
        for node_number in matched_node_numbers:
            result.append(ve("The morphology needs to have one soma node", node_number, "Error"))

    return result


def validate_expected_types(node):

    """ This function validates the expected types of the nodes """

    result = []

    if node['type'] not in valid_types:
        result.append(ve("Node type needs to be one of these values: %s" % valid_types, node['id'], "Warning"))

    return result


def validate_node_parent(morphology, node):

    """ This function validates the type of parent node for a specific type of child node """

    result = []
    valid_soma_parents = {None}
    valid_axon_parents = {SOMA, AXON, BASAL_DENDRITE, None}
    valid_basal_dendrite_parents = {SOMA, BASAL_DENDRITE}
    valid_apical_dendrite_parents = {SOMA, APICAL_DENDRITE}

    if node['type'] == SOMA:
        if morphology.parent_of(node):
            result.append(ve("Type 1 can only have a parent of the following types: %s" % valid_soma_parents
                             , node['id'], "Warning"))
    if node['type'] == AXON:
        if morphology.parent_of(node):
            if morphology.parent_of(node)['type'] not in valid_axon_parents:
                result.append(ve("Type 2 can only have a parent of the following types: %s" % valid_axon_parents
                                 , node['id'], "Warning"))
    if node['type'] == BASAL_DENDRITE:
        parent = morphology.parent_of(node)
        if not parent or parent['type'] not in valid_basal_dendrite_parents:
            result.append(ve("Type 3 can only have a parent of the following types: %s" % valid_basal_dendrite_parents
                             , node['id'], "Warning"))
    if node['type'] == APICAL_DENDRITE:
        parent = morphology.parent_of(node)
        if not parent or parent['type'] not in valid_apical_dendrite_parents:
            result.append(ve("Type 4 can only have a parent of the following types: %s" % valid_apical_dendrite_parents
                             , node['id'], "Warning"))

    return result


def validate_immediate_children_of_soma_cannot_branch(morphology, node):

    """ This function validates that immediate children of soma cannot branch """

    result = []

    if morphology.parent_of(node):
        if morphology.parent_of(node)['type'] == SOMA:
            if len(morphology.children_of(node)) > 1:
                result.append(ve("Immediate children of soma cannnot branch", node['type'], "Error"))

    return result


def validate(morphology):

    result = []

    for node in morphology.nodes():
        result += validate_expected_types(node)

        result += validate_node_parent(morphology, node)

        result += validate_immediate_children_of_soma_cannot_branch(morphology, node)

    """ nodes that are type 4 can only have one parent parent of type 1 """
    result += validate_count_node_parent(morphology, APICAL_DENDRITE, SOMA, 1)

    """ There can only be one node of type 1 """
    result += validate_number_of_soma_nodes(morphology)

    return result
