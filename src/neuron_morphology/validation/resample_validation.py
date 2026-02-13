from neuron_morphology.validation.result import NodeValidationError as ve
from neuron_morphology.constants import *


def validate_distance_between_connected_nodes(morphology):

    result = []
    for compartment in morphology.compartments:
        node1 = compartment[0]
        node2 = compartment[1]
        if node1['type'] is not SOMA and node2['type'] is not SOMA:
            if morphology.get_compartment_length(compartment) > 50.0:
                result.append(ve("The distance between two nodes should be less than 50px", [node1['id'], node2['id']],
                                 "Error"))

    return result


def validate(morphology):

    result = []

    result += validate_distance_between_connected_nodes(morphology)

    return result
