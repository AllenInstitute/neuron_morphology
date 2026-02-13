from neuron_morphology.validation.result import NodeValidationError as ve


def validate_children_nodes_appear_before_parent_nodes(morphology):

    result = []
    nodes = morphology.nodes()

    for node in nodes:
        parent = morphology.parent_of(node)
        if parent and node['id'] < parent['id']:
            result.append(ve("Child node needs to come before parent node", node['id'], "Error"))

    return result


def validate(morphology):

    result = []

    result += validate_children_nodes_appear_before_parent_nodes(morphology)

    return result
