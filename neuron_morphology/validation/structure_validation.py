from result import NodeValidationError as ve


def validate_children_nodes_appear_before_parent_nodes(morphology):

    result = []

    for tree in range(0, morphology.num_trees):
        for tree_node in morphology.tree(tree):
            parent = morphology.parent_of(tree_node)
            if parent and tree_node.original_n < parent.original_n:
                result.append(ve("Child node needs to come before parent node", tree_node.original_n, "Error"))

    return result


def validate(morphology):

    result = []

    result += validate_children_nodes_appear_before_parent_nodes(morphology)

    return result
