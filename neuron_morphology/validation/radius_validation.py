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

from errors import ValidationError as ve
from neuron_morphology.constants import *


def validate_node_radius(node):

    """ This function validates the radius for types 1, 3, and 4 """

    errors = []

    soma_radius_threshold = 35
    basal_dendrite_apical_dendrite_radius_threshold = 30

    if node.t == 1:
        if node.radius < soma_radius_threshold:
            errors.append(ve("The radius must be above %spx for type 1" % soma_radius_threshold, node.original_n, False))
    if node.t == 3 or node.t == 4:
        if node.radius > basal_dendrite_apical_dendrite_radius_threshold:
            errors.append(ve("The radius must be below %spx for types 3 and 4" % basal_dendrite_apical_dendrite_radius_threshold
                             , node.original_n, False))

    return errors


def validate(morphology):

    errors = []

    for tree in range(0, morphology.num_trees):
        for tree_node in morphology.tree(tree):
            errors += validate_node_radius(tree_node)

    return errors
