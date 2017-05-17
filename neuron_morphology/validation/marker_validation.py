import sys

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

from result import MarkerValidationError as ve
from neuron_morphology.constants import *


def validate_coordinates_corresponding_to_dendrite_tip(marker_file, morphology):

    """ This function checks whether the coordinates for each dendrite marker
        corresponds to a tip of a dendrite type in the related morphology """

    result = []
    marker_types = [CUT_DENDRITE]
    morphology_tip_nodes = []
    morphology_dendrite_nodes = morphology.node_list_by_type(BASAL_DENDRITE) + morphology.node_list_by_type(APICAL_DENDRITE)
    for node in morphology_dendrite_nodes:
        if len(morphology.children_of(node)) == 0:
            morphology_tip_nodes.append(node)

    for marker in marker_file:
        if marker['name'] in marker_types:
            for node in morphology_tip_nodes:
                if marker['x'] != node.x or marker['y'] != node.y or marker['z'] != node.z:
                    result.append(ve("Coordinates for each dendrite (type 10) needs to correspond to "
                                     "a tip of a dendrite type (type 3 or 4) in the related morphology", marker, "Medium"))

    return result


def validate_expected_name(marker_file):

    """ This function checks whether the markers have the expected types """

    result = []
    valid_names = [CUT_DENDRITE, NO_RECONSTRUCTION, TYPE_30]

    for marker in marker_file:
        if marker['name'] not in valid_names:
            result.append(ve("Marker name needs to be one of these values: %s" % valid_names, marker, "Medium"))

    return result


def validate_type_thirty_count(marker_file):

    """ This function checks whether there is exactly one type 30 in the file """

    result = []
    count = 0
    type_30_markers = []

    for marker in marker_file:
        if marker['name'] is TYPE_30:
            count += 1
            type_30_markers.append(marker)

    if count > 1:
        result.append(ve("Total number of type 30s is %s" % count, type_30_markers, "Medium"))
    if count < 1:
        result.append(ve("Total number of type 30s is %s" % count, [], "Medium"))

    return result


def validate_no_reconstruction_count(marker_file):

    """ This function checks whether there is exactly one type 20 in the file """

    result = []
    count = 0
    no_reconstruction_markers = []

    for marker in marker_file:
        if marker['name'] is NO_RECONSTRUCTION:
            count += 1
            no_reconstruction_markers.append(marker)

    if count > 1:
        result.append(ve("Total number of type 20s is more than one: %s" % count, no_reconstruction_markers, "Warning"))

    return result


def validate(marker_file, morphology):

    result = []

    result += validate_expected_name(marker_file)
    result += validate_coordinates_corresponding_to_dendrite_tip(marker_file, morphology)
    result += validate_no_reconstruction_count(marker_file)
    result += validate_type_thirty_count(marker_file)

    return result
