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
from neuron_morphology.constants import *


def validate_independent_axon_has_more_than_four_nodes(morphology):

    """ This function checks if an independent (parent is -1)
        axon has more than three nodes """

    errors = []
    axon_nodes = morphology.node_list_by_type(AXON)

    for node in axon_nodes:
        if morphology.parent_of(node) is None:
            if len(morphology.children_of(node)) == 0:
                    errors.append(ve("There is an independent axon with less than 4 nodes", node.original_n, "Low"))

            elif len(morphology.children_of(node)) == 1:
                if len(morphology.children_of(morphology.children_of(node)[0])) == 0:
                        errors.append(ve("There is an independent axon with less than 4 nodes"
                                         , node.original_n, "Low"))

                elif len(morphology.children_of(morphology.children_of(node)[0])) == 1:
                    if len(morphology.children_of(morphology.children_of(morphology.children_of(node)[0])[0])) == 0:
                        errors.append(ve("There is an independent axon with less than 4 nodes"
                                         , node.original_n, "Low"))

            elif len(morphology.children_of(node)) == 2:
                if len(morphology.children_of(morphology.children_of(node)[0])) == 0 and \
                                len(morphology.children_of(morphology.children_of(node)[1])) == 0:
                    errors.append(ve("There is an independent axon with less than 4 nodes", node.original_n, "Low"))

    return errors


def count_number_of_independent_axons(morphology):

    """ This functions counts the number of independent axons (parent is -1) """

    errors = []
    count = 0
    axon_nodes = morphology.node_list_by_type(AXON)
    independent_axon_node_ids = []

    for node in axon_nodes:
        if morphology.parent_of(node) is None:
            count += 1
            independent_axon_node_ids.append(node.original_n)

    errors.append(ve("Total number of independent axons: %s" % count, independent_axon_node_ids, "Low"))

    return errors


def validate_types_three_four_traceable_back_to_soma(morphology):

    """ This function checks if types 3,4 are traceable 
        back to soma """

    errors = []
    traceable_types = {BASAL_DENDRITE, APICAL_DENDRITE}

    traceable_nodes = set()
    to_visit = {morphology.soma_root()}
    while to_visit:
        node = to_visit.pop()
        traceable_nodes.add(node)
        to_visit.update(morphology.children_of(node))

    must_be_traceable = []
    for node in reduce(list.__add__, map(morphology.node_list_by_type, traceable_types)):
        must_be_traceable.append(node)
    for node in must_be_traceable:
        if node not in traceable_nodes:
            errors.append(ve("Nodes of type %s must be traceable back to the soma" % traceable_types,
                             node.original_n, "Medium"))

    return errors


def validate(morphology):

    errors = []

    errors += validate_independent_axon_has_more_than_four_nodes(morphology)

    errors += validate_types_three_four_traceable_back_to_soma(morphology)

    errors += count_number_of_independent_axons(morphology)

    return errors
