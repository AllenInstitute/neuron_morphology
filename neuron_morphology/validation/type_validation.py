from neuron_morphology.validation.result import NodeValidationError as ve
from neuron_morphology.constants import *

valid_types = {SOMA, AXON, BASAL_DENDRITE, APICAL_DENDRITE}


def validate_count_node_parent(morphology, node_type, parent_type, expected_count):

    """ This function validates the number of nodes that have a specific type of parent """

    matched_node_numbers = []
    result = []

    nodes_by_type = morphology.get_node_by_types([node_type])
    for node in nodes_by_type:
        if morphology.parent_of(node) and morphology.parent_of(node)['type'] is parent_type:
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

    soma = morphology.get_node_by_types([SOMA])

    if len(soma) != 1:
        for node in soma:
            result.append(ve("The morphology needs to have one soma node", node['id'], "Error"))

    return result


def validate_expected_types(morphology):

    """ This function validates the expected types of the nodes """

    result = []

    nodes_with_invalid_type = morphology.filter_nodes(lambda node: node['type'] not in valid_types)
    for node in nodes_with_invalid_type:
        result.append(ve("Node type needs to be one of these values: %s" % valid_types, node['id'], "Warning"))

    return result


def valid_dendrite_parent(morphology, node, valid_parent_type):

    parent = morphology.parent_of(node)
    return parent and parent['type'] in valid_parent_type


def validate_node_parent(morphology):

    """ This function validates the type of parent node for a specific type of child node """

    result = []
    valid_soma_parents = {None}
    valid_axon_parents = {SOMA, AXON, BASAL_DENDRITE, None}
    valid_basal_dendrite_parents = {SOMA, BASAL_DENDRITE}
    valid_apical_dendrite_parents = {SOMA, APICAL_DENDRITE}

    soma_node_with_invalid_parents = morphology.filter_nodes(lambda node: node['type'] == SOMA and
                                                                          morphology.parent_of(node))
    if soma_node_with_invalid_parents:
        result.append(ve("Type 1 can only have a parent of the following types: %s" % valid_soma_parents,
                         soma_node_with_invalid_parents[0]['id'], "Error"))

    axon_nodes_with_invalid_parents = morphology.filter_nodes(lambda node: node['type'] == AXON and
                                                                           morphology.parent_of(node) and
                                                                           morphology.parent_of(node)['type']
                                                                           not in valid_axon_parents)

    for node in axon_nodes_with_invalid_parents:
        result.append(ve("Type 2 can only have a parent of the following types: %s" % valid_axon_parents, node['id'],
                         "Error"))

    basal_dendrite_nodes = morphology.get_node_by_types([BASAL_DENDRITE])

    for node in basal_dendrite_nodes:
        if not valid_dendrite_parent(morphology, node, valid_basal_dendrite_parents):
            result.append(ve("Type 3 can only have a parent of the following types: %s" % valid_basal_dendrite_parents,
                             node['id'], "Error"))

    apical_dendrite_nodes = morphology.get_node_by_types([APICAL_DENDRITE])
    for node in apical_dendrite_nodes:
        if not valid_dendrite_parent(morphology, node, valid_apical_dendrite_parents):
            result.append(ve("Type 4 can only have a parent of the following types: %s" % valid_apical_dendrite_parents,
                             node['id'], "Error"))

    return result


def validate_immediate_children_of_soma_cannot_branch(morphology):

    """ This function validates that immediate children of soma cannot branch """

    result = []

    soma = morphology.get_root()
    if soma:
        soma_children = morphology.children_of(soma)
        for node in soma_children:
            if len(morphology.children_of(node)) > 1:
                result.append(ve("Immediate children of soma cannot branch", node['id'], "Error"))

    return result


def validate_multiple_axon_initiation_points(morphology):

    """ This function validates that the parent of axon (either type 1 or 3) only happens once """

    nodes = morphology.nodes()
    expected_count = 1
    matched_node_numbers = []
    result = []
    for node in nodes:
        if node['type'] == AXON:
            parent = morphology.parent_of(node)
            if parent and parent['type'] in [BASAL_DENDRITE, SOMA]:
                matched_node_numbers.append(node['id'])

    if len(matched_node_numbers) > expected_count:
        for node_number in matched_node_numbers:
            result.append(ve("Axon can only have one parent of type basal dendrite or soma", node_number, "Error"))

    return result


def validate(morphology):

    result = []

    result += validate_expected_types(morphology)

    result += validate_node_parent(morphology)

    result += validate_immediate_children_of_soma_cannot_branch(morphology)

    """ nodes that are type 4 can only have one parent parent of type 1 """
    result += validate_count_node_parent(morphology, APICAL_DENDRITE, SOMA, 1)

    """ There can only be one node of type 1 """
    result += validate_number_of_soma_nodes(morphology)

    result += validate_multiple_axon_initiation_points(morphology)

    return result
