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

from errors import NodeValidationError as ve


def validate_distance_between_connected_nodes(morphology):

    errors = []

    for comp in range(0, len(morphology.compartment_list)):
        if 9.0 > morphology.compartment(comp).length or morphology.compartment(comp).length > 11.0:
            errors.append(ve("The distance between two nodes should be approximately 10px", [morphology.compartment(comp)
                             .node1.original_n, morphology.compartment(comp).node2.original_n], "Medium"))

    return errors


def validate(morphology):

    errors = []

    errors += validate_distance_between_connected_nodes(morphology)

    return errors
