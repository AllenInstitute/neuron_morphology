from neuron_morphology.validation.result import NodeValidationError as ve
from neuron_morphology.constants import *
from functools import reduce


def validate_independent_axon_has_more_than_four_nodes(morphology):

    """ This function checks if an independent (parent is -1)
        axon has more than three nodes """

    result = []
    axon_nodes = morphology.get_node_by_types([AXON])

    for node in axon_nodes:
        if morphology.parent_of(node) is None:
            if len(morphology.children_of(node)) == 0:
                result.append(ve("There is an independent axon with less than 4 nodes", node['id'], "Info"))

            elif len(morphology.children_of(node)) == 1:
                if len(morphology.children_of(morphology.children_of(node)[0])) == 0:
                    result.append(ve("There is an independent axon with less than 4 nodes", node['id'], "Info"))

                elif len(morphology.children_of(morphology.children_of(node)[0])) == 1:
                    if len(morphology.children_of(morphology.children_of(morphology.children_of(node)[0])[0])) == 0:
                        result.append(ve("There is an independent axon with less than 4 nodes", node['id'], "Info"))

            elif len(morphology.children_of(node)) == 2:
                if len(morphology.children_of(morphology.children_of(node)[0])) == 0 and \
                                len(morphology.children_of(morphology.children_of(node)[1])) == 0:
                    result.append(ve("There is an independent axon with less than 4 nodes", node['id'], "Info"))

    return result


def validate_types_three_four_traceable_back_to_soma(morphology):

    """ This function checks if types 3,4 are traceable
        back to soma """

    result = []
    traceable_types = {BASAL_DENDRITE, APICAL_DENDRITE}

    traceable_nodes = set()
    to_visit = [morphology.get_root()]
    while to_visit:
        node = to_visit.pop()
        traceable_nodes.add(node['id'])
        to_visit.extend(morphology.children_of(node))

    must_be_traceable = []
    for node in reduce(list.__add__, map(morphology.get_node_by_types, [traceable_types])):
        must_be_traceable.append(node['id'])
    for node_id in must_be_traceable:
        if node_id not in traceable_nodes:
            result.append(ve("Nodes of type %s must be traceable back to the soma" % traceable_types, node_id,
                             "Warning"))

    return result


def validate(morphology):

    result = []

    result += validate_independent_axon_has_more_than_four_nodes(morphology)

    result += validate_types_three_four_traceable_back_to_soma(morphology)

    return result

