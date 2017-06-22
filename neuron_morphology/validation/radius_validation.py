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

from result import NodeValidationError as ve
import numpy as np
from neuron_morphology.constants import *


def validate_node_type_radius(node):

    """ This function validates the radius for types 1, 3, and 4 """

    result = []

    soma_radius_threshold = 35
    basal_dendrite_apical_dendrite_radius_threshold = 20

    if node.t == SOMA:
        if node.radius < soma_radius_threshold:
            result.append(ve("The radius must be above %spx for type 1" % soma_radius_threshold, node.original_n
                             , "Info"))
    if node.t == BASAL_DENDRITE or node.t == APICAL_DENDRITE:
        if node.radius > basal_dendrite_apical_dendrite_radius_threshold:
            result.append(ve("The radius must be below %spx for types 3 and 4"
                             % basal_dendrite_apical_dendrite_radius_threshold
                             , node.original_n, "Info"))

    return result


def validate_extreme_taper(morphology):

    """ This function checks whether there is an extreme taper.
        Extreme taper occurs when for each segment, the average
        radius of the first two nodes is more than two times the
        average radius of the last two nodes.
         
         Note: This test is limited to segments of at lease 8 nodes. """

    result = []

    for segment_list in morphology.segment_lists:
        for segment in segment_list:
            nodes_in_segment = segment.node_list

            if len(nodes_in_segment) > 7:
                if nodes_in_segment[0].t in [BASAL_DENDRITE, APICAL_DENDRITE]:

                    average_radius_beg = (nodes_in_segment[0].radius + nodes_in_segment[1].radius)/2
                    average_radius_end = (nodes_in_segment[-1].radius + nodes_in_segment[-2].radius)/2

                    if average_radius_beg > 4 * average_radius_end:
                        result.append(ve("Extreme Taper: For types 3 and 4, the average radius of the first two nodes "
                                         "in a segment should not be greater than four times the average radius of the "
                                         "last two nodes in a segment (For segments that have more than 8 nodes)"
                                         , [nodes_in_segment[0].original_n, nodes_in_segment[-2].original_n], "Info"))

    return result


def validate_radius_has_negative_slope_dendrite(morphology, dendrite):

    """ This function checks whether the radius for dendrite nodes decreases
        when you are going away from the soma. """

    result = []

    branch_order = dict()
    to_visit = {morphology.soma_root()}

    while to_visit:
        node = to_visit.pop()
        if morphology.parent_of(node) and len(morphology.children_of(node)) > 1:
            branch_order[node] = branch_order[morphology.parent_of(node)] + 1
        elif morphology.parent_of(node) and len(morphology.children_of(node)) <= 1:
            branch_order[node] = branch_order[morphology.parent_of(node)]
        elif not morphology.parent_of(node):
            branch_order[node] = 1
        to_visit.update(morphology.children_of(node))

    dendrite_nodes_in_morphology = morphology.node_list_by_type(dendrite)
    if dendrite_nodes_in_morphology:
        nodes_by_branch_order = dict()
        for node, order in branch_order.iteritems():
            if node.t == dendrite:
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

        if len(orders) > 1:
            if slope_linear_regression_branch_order_avg_radius(orders, avg_radius) >= 0:
                result.append(ve("Radius should have a negative slope for the following type: %s" % dendrite, [], "Warning"))

    return result


def slope_linear_regression_branch_order_avg_radius(orders, avg_radius):

    """ Use linear regression to find the slope of the best fit line """

    m = 0

    if len(avg_radius) != 0:
        x = np.array(orders)
        y = np.array(avg_radius)

        a = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(a, y)[0]

    return m


def validate_constrictions(morphology):

    """ This function checks if the radius of basal dendrite and apical dendrite 
        nodes is smaller 2.0px """

    result = []

    depth = dict()
    to_visit = {morphology.soma_root()}
    while to_visit:
        node = to_visit.pop()
        if morphology.parent_of(node):
            depth[node] = depth[morphology.parent_of(node)] + 1
        else:
            depth[node] = 0
        to_visit.update(morphology.children_of(node))

    eligible_nodes = sorted([node for node in depth.keys() if depth[node] < 10])
    for node in eligible_nodes:
        if node.t in [BASAL_DENDRITE, APICAL_DENDRITE]:
            if node.radius < 2.0:
                result.append(ve("Constriction: The radius of types 3 and 4 should not be less than 2.0px"
                                 , node.original_n, "Warning"))

    return result


def validate(morphology):

    result = []

    for tree in range(0, morphology.num_trees):
        for tree_node in morphology.tree(tree):
            result += validate_node_type_radius(tree_node)

    result += validate_constrictions(morphology)

    result += validate_extreme_taper(morphology)

    result += validate_radius_has_negative_slope_dendrite(morphology, BASAL_DENDRITE)

    result += validate_radius_has_negative_slope_dendrite(morphology, APICAL_DENDRITE)

    return result
