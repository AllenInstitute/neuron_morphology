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
import numpy as np
from neuron_morphology.constants import *


def validate_node_type_radius(node):

    """ This function validates the radius for types 1, 3, and 4 """

    errors = []

    soma_radius_threshold = 35
    basal_dendrite_apical_dendrite_radius_threshold = 30

    if node.t == SOMA:
        if node.radius < soma_radius_threshold:
            errors.append(ve("The radius must be above %spx for type 1" % soma_radius_threshold, node.original_n
                             , False))
    if node.t == BASAL_DENDRITE or node.t == APICAL_DENDRITE:
        if node.radius > basal_dendrite_apical_dendrite_radius_threshold:
            errors.append(ve("The radius must be below %spx for types 3 and 4"
                             % basal_dendrite_apical_dendrite_radius_threshold
                             , node.original_n, "Medium"))

    return errors


def validate_extreme_taper(morphology):

    """ This function checks whether there is an extreme taper.
        Extreme taper occurs when for each segment, the average
        radius of the first two nodes is more than two times the
        average radius of the last two nodes.
         
         Note: This test is limited to segments of at lease 8 nodes. """

    errors = []

    for segment_list in morphology.segment_lists:
        for segment in segment_list:
            nodes_in_segment = segment.node_list

            if len(nodes_in_segment) > 7:
                if nodes_in_segment[0].t in [BASAL_DENDRITE, APICAL_DENDRITE]:

                    average_radius_beg = (nodes_in_segment[0].radius + nodes_in_segment[1].radius)/2
                    average_radius_end = (nodes_in_segment[-1].radius + nodes_in_segment[-2].radius)/2

                    if average_radius_beg > 2 * average_radius_end:
                        errors.append(ve("Extreme Taper: For types 3 and 4, the average radius of the first two nodes"
                                         "in a segment should not be greater than twice the average radius of the last"
                                         "two nodes in a segment (For segments that have more than 8 nodes)"
                                         , [nodes_in_segment[0].original_n, nodes_in_segment[-2].original_n], "Low"))

    return errors


def validate_dendrite_radius_decreases_going_away_from_soma(morphology):

    """ This function checks whether the radius for dendrite nodes decreases
        when you are going away from the soma. """

    errors = []

    branch_order = dict()
    to_visit = {morphology.soma_root()}
    while to_visit:
        node = to_visit.pop()
        if morphology.parent_of(node):
            branch_order[node] = branch_order[morphology.parent_of(node)] + 1
        else:
            branch_order[node] = 0
        to_visit.update(morphology.children_of(node))

    nodes_by_branch_order = dict()
    for node, order in branch_order.iteritems():
        if node.t in [BASAL_DENDRITE, APICAL_DENDRITE]:
            nodes_by_branch_order[order] = nodes_by_branch_order.get(order, [])
            nodes_by_branch_order[order].append(node)

    orders = sorted(nodes_by_branch_order.keys())
    avg_radius = []
    for order in orders:
        nodes = nodes_by_branch_order[order]
        total_radius = 0
        for node in nodes:
            total_radius += node.radius
        avg_radius.append(total_radius / len(nodes))

    dendrite_nodes = morphology.node_list_by_type(BASAL_DENDRITE) + morphology.node_list_by_type(APICAL_DENDRITE)
    dendrite_node_ids = [node.original_n for node in dendrite_nodes]

    # Use linear regression to find the slope of the best fit line
    if len(orders) != 0 and len(avg_radius) != 0:
        x = np.array(orders)
        y = np.array(avg_radius)

        a = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(a, y)[0]

        if m >= 0:
            errors.append(ve("Radius should decrease when you are going away from the soma", dendrite_node_ids, "Medium"))

    return errors


def validate_constrictions(morphology, node):

    """ This function checks if the radius of basal dendrite and apical dendrite 
        nodes is smaller than their immediate child """

    errors = []

    if node.t in [BASAL_DENDRITE, APICAL_DENDRITE]:
        if node.radius < 1.5:
            for child in morphology.children_of(node):
                if node.radius < child.radius:
                    errors.append(ve("Constriction: The radius of types 3 and 4 should not be "
                                     "smaller than the radius of their immediate child", child.original_n, "Medium"))

    return errors


def validate(morphology):

    errors = []

    for tree in range(0, morphology.num_trees):
        for tree_node in morphology.tree(tree):
            errors += validate_node_type_radius(tree_node)

            errors += validate_constrictions(morphology, tree_node)

    errors += validate_extreme_taper(morphology)

    errors += validate_dendrite_radius_decreases_going_away_from_soma(morphology)

    return errors
