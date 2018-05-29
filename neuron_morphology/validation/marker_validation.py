from neuron_morphology.validation.result import MarkerValidationError as ve
from neuron_morphology.constants import *


def validate_coordinates_corresponding_to_dendrite_tip(marker_file, morphology):

    """ This function checks whether the coordinates for each dendrite marker
        corresponds to a tip of a dendrite type in the related morphology """

    result = []
    marker_types = [CUT_DENDRITE]
    morphology_tip_nodes = []
    morphology_dendrite_nodes = morphology.get_node_by_types([BASAL_DENDRITE, APICAL_DENDRITE])

    for node in morphology_dendrite_nodes:
        if not morphology.children_of(node):
            morphology_tip_nodes.append(node)

    for marker in marker_file:
        tip_marker = False
        if marker['name'] in marker_types:
            for node in morphology_tip_nodes:

                """ Subtract one from the coordinates because there is a known discrepancy between the coordinates of 
                    the marker file and the swc file
                """
                if (marker['original_x'] - 1) == node['x'] and (marker['original_y'] - 1) == node['y'] and (marker['original_z'] - 1) == node['z']:
                    tip_marker = True
            if not tip_marker:
                result.append(ve("Coordinates for each dendrite (type 10) needs to correspond to a tip of a dendrite "
                                 "type (type 3 or 4) in the related morphology", {'x': marker['original_x'],
                                                                                  'y': marker['original_y'],
                                                                                  'z': marker['original_z'],
                                                                                  'name': marker['name']}, "Info"))

    return result


def validate_coordinates_corresponding_to_axon_tip(marker_file, morphology):

    """ This function checks whether the coordinates for each axon marker
        corresponds to a tip of a axon type in the related morphology """

    result = []
    marker_types = [NO_RECONSTRUCTION]
    morphology_tip_nodes = []
    morphology_axon_nodes = morphology.get_node_by_types([AXON])

    for node in morphology_axon_nodes:
        if not morphology.children_of(node):
            morphology_tip_nodes.append(node)

    for marker in marker_file:
        tip_marker = False
        if marker['name'] in marker_types:
            for node in morphology_tip_nodes:

                """ Subtract one from the coordinates because there is a known discrepancy between the coordinates of 
                    the marker file and the swc file
                """
                if (marker['original_x'] - 1) == node['x'] and (marker['original_y'] - 1) == node['y'] \
                    and (marker['original_z'] - 1) == node['z']:
                    tip_marker = True
            if not tip_marker:
                result.append(ve("Coordinates for each axon (type 20) needs to correspond to a tip of an axon "
                                 "type (type 2) in the related morphology", {'x': marker['original_x'],
                                                                             'y': marker['original_y'],
                                                                             'z': marker['original_z'],
                                                                             'name': marker['name']}, "Info"))

    return result


def validate_expected_name(marker_file):

    """ This function checks whether the markers have the expected types """

    result = []
    valid_names = [CUT_DENDRITE, NO_RECONSTRUCTION, TYPE_30]

    for marker in marker_file:
        if marker['name'] not in valid_names:
            result.append(ve("Marker name needs to be one of these values: %s" % valid_names, {'x': marker['original_x'],
                                                                                               'y': marker['original_y'],
                                                                                               'z': marker['original_z'],
                                                                                               'name': marker['name']},
                             "Warning"))

    return result


def validate_type_thirty_count(marker_file):

    """ This function checks whether there is exactly one type 30 in the file """

    result = []
    type_30_markers = []

    for marker in marker_file:
        if marker['name'] is TYPE_30:
            type_30_markers.append(marker)

    if len(type_30_markers) > 1:
        for marker in type_30_markers:
            result.append(ve("Total number of type 30s is %s" % len(type_30_markers), {'x': marker['original_x'],
                                                                                       'y': marker['original_y'],
                                                                                       'z': marker['original_z'],
                                                                                       'name': marker['name']},
                             "Warning"))
    if len(type_30_markers) < 1:
        result.append(ve("Total number of type 30s is %s" % len(type_30_markers), {}, "Warning"))

    return result


def validate_no_reconstruction_count(marker_file):

    """ This function checks whether there is exactly one type 20 in the file """

    result = []
    no_reconstruction_markers = []

    for marker in marker_file:
        if marker['name'] is NO_RECONSTRUCTION:
            no_reconstruction_markers.append(marker)

    if len(no_reconstruction_markers) > 1:
        for marker in no_reconstruction_markers:
            result.append(ve("Total number of type 20s is more than one: %s" % len(no_reconstruction_markers),
                             {'x': marker['original_x'], 'y': marker['original_y'], 'z': marker['original_z'],
                              'name': marker['name']}, "Warning"))

    return result


def validate(marker_file, morphology):

    result = []

    result += validate_expected_name(marker_file)
    result += validate_coordinates_corresponding_to_dendrite_tip(marker_file, morphology)
    result += validate_coordinates_corresponding_to_axon_tip(marker_file, morphology)
    result += validate_no_reconstruction_count(marker_file)
    result += validate_type_thirty_count(marker_file)

    return result
