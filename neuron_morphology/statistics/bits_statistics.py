from neuron_morphology.constants import *


def count_number_of_independent_axons(morphology):

    """ This functions counts the number of independent axons (parent is -1) """

    count = 0
    axon_nodes = morphology.get_node_by_types([AXON])

    for node in axon_nodes:
        if morphology.parent_of(node) is None:
            count += 1

    return count


def statistics(morphology):

    stats = {"Number of Independent Axons": count_number_of_independent_axons(morphology)}

    return stats
