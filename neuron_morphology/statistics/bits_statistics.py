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

from neuron_morphology.constants import *


def count_number_of_independent_axons(morphology):

    """ This functions counts the number of independent axons (parent is -1) """

    count = 0
    axon_nodes = morphology.node_list_by_type(AXON)

    for node in axon_nodes:
        if morphology.parent_of(node) is None:
            count += 1

    return count


def statistics(morphology):

    stats = {}

    stats["Number of Independent Axons"] = count_number_of_independent_axons(morphology)

    return stats
