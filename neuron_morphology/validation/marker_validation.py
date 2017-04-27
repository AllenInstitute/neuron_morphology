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

from errors import MarkerValidationError as ve
from neuron_morphology.constants import *


def validate_coordinates_corresponding_to_dendrite_tip(marker_file, morphology):

    """ This function checks whether the coordinates for each dendrite marker
        corresponds to a tip of a dendrite type in the related morphology """

    errors = []
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
                    errors.append(ve("Coordinates for each dendrite (type 10) needs to correspond to "
                                     "a tip of a dendrite type in the related morphology", marker, "Medium"))

    return errors


def validate_expected_name(marker_file):

    """ This function checks whether the markers have the expected types """

    errors = []
    valid_names = [CUT_DENDRITE, NO_RECONSTRUCTION, TYPE_30]

    for marker in marker_file:
        if marker['name'] not in valid_names:
            errors.append(ve("Marker name needs to be one of these values: %s" % valid_names, marker, "Medium"))

    return errors


def validate(marker_file, morphology):

    errors = []

    errors += validate_expected_name(marker_file)
    errors += validate_coordinates_corresponding_to_dendrite_tip(marker_file, morphology)

    return errors