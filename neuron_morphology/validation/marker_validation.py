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


def validate_coordinates_corresponding_dendrite_tip(marker_file, morphology):

    """ This function checks whether the coordinates for each dendrite
        corresponds to a tip of dendrite type in the related morphology """

    errors = []
    marker_types = [CUT_DENDRITE]
    morphology_tip_type = [BASAL_DENDRITE, APICAL_DENDRITE]
    morphology_tip_nodes = []
    morphology_dendrite_nodes = morphology.node_list_by_type(BASAL_DENDRITE)\
        .append(morphology.node_list_by_type(APICAL_DENDRITE))

    for node in morphology_dendrite_nodes:
        if len(morphology.children_of(node)) == 0:
            morphology_tip_nodes.append(node)

    #for marker in marker_file:
     #   if marker_type in marker_types:


def validate_expected_name(marker_file):

    """ This function checks whether the markers have the expected types """

    errors = []
    valid_names = [CUT_DENDRITE, NO_RECONSTRUCTION, TYPE_30]

    for marker in marker_file:
        if marker['name'] not in valid_names:
            errors.append(ve("Marker name needs to be one of these values: %s" % valid_names, marker, False))

    return errors


def validate(marker_file, morphology):

    errors = []

    errors += validate_expected_name(marker_file)
    errors += validate_coordinates_corresponding_dendrite_tip(marker_file, morphology)

    return errors




def validate_marker(fname):
    print("Evaluating '%s'" % fname)
    err = False
    # make sure the name contains 'marker'
    if len(fname.split('marker')) == 1:
        print("ERROR: File name does not contain string 'marker'.")
        err = True
    # make sure there are an appropriate number of columns
    with open(fname, "r") as f:
        cnt = 0
        line_err = False
        while True:
            line = f.readline()
            if len(line) == 0:
                break
            cnt += 1
            if line[0] == '#':
                continue
            cols = line.split(',')
            if len(cols) != 10 and not line_err:
                print("ERROR: Line %d has %d CSV column(s). Expected 10." % (cnt, len(cols)))
                err = True
                line_err = True
    if not err:
        print("OK")
    # TODO consider looking for a node for each marker point in the associated
    #   SWC file
    return err