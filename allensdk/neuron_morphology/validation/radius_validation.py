from result import NodeValidationError as ve
import numpy as np
from allensdk.neuron_morphology.constants import *


def validate_node_type_radius(morphology):

    """ This function validates the radius for types 1, 3, and 4 """

    result = []

    soma_radius_threshold = 35
    basal_dendrite_apical_dendrite_radius_threshold = 20
    for node in morphology.nodes():
        if node['type'] is SOMA:
            if node['radius'] < soma_radius_threshold:
                result.append(ve("The radius must be above %spx for type 1" % soma_radius_threshold, node['id'],
                                 "Info"))
        if node['type'] is BASAL_DENDRITE or node['type'] is APICAL_DENDRITE:
            if node['radius'] > basal_dendrite_apical_dendrite_radius_threshold:
                result.append(ve("The radius must be below %spx for types 3 and 4"
                                 % basal_dendrite_apical_dendrite_radius_threshold, node['id'], "Info"))

    return result


def validate_extreme_taper(morphology):

    """ This function checks whether there is an extreme taper.
        Extreme taper occurs when for each segment, the average
        radius of the first two nodes is more than two times the
        average radius of the last two nodes.

         Note: This tests is limited to segments of at lease 8 nodes. """

    result = []

    for segment in morphology.get_segment_list():
        print(segment)
        nodes_in_segment = segment

        print(nodes_in_segment)
        if len(nodes_in_segment) > 7:
            if nodes_in_segment[0]['type'] in [BASAL_DENDRITE, APICAL_DENDRITE]:

                average_radius_beg = (nodes_in_segment[0]['radius'] + nodes_in_segment[1]['radius'])/2
                average_radius_end = (nodes_in_segment[-1]['radius'] + nodes_in_segment[-2]['radius'])/2

                if average_radius_beg > 4 * average_radius_end:
                    result.append(ve("Extreme Taper: For types 3 and 4, the average radius of the first two nodes "
                                     "in a segment should not be greater than four times the average radius of the "
                                     "last two nodes in a segment (For segments that have more than 8 nodes)",
                                     [nodes_in_segment[0]['id'], nodes_in_segment[-2]['id']], "Info"))

    return result


def validate_radius_has_negative_slope_dendrite(morphology, dendrite):

    """ This function checks whether the radius for dendrite nodes decreases
        when you are going away from the soma. """

    result = []

    branch_order = []
    to_visit = [morphology.get_root()]

    while to_visit:
        node = to_visit.pop()
        parent_node_branch_order = [item[1] for item in branch_order if item[0] is morphology.parent_of(node)]
        if morphology.parent_of(node) and len(morphology.children_of(node)) > 1:
            branch_order.append((node, parent_node_branch_order[0] + 1))
        elif morphology.parent_of(node) and len(morphology.children_of(node)) <= 1:
            branch_order.append((node, parent_node_branch_order[0]))
        elif not morphology.parent_of(node):
            branch_order.append((node, 1))
        to_visit.extend(morphology.children_of(node))

    dendrite_nodes_in_morphology = morphology.get_node_by_type(dendrite)
    if dendrite_nodes_in_morphology:
        nodes_by_branch_order = dict()
        for node, order in branch_order:
            if node['type'] == dendrite:
                nodes_by_branch_order[order] = nodes_by_branch_order.get(order, [])
                nodes_by_branch_order[order].append(node)

        orders = sorted(nodes_by_branch_order.keys())
        avg_radius = []

        for order in orders:
            nodes = nodes_by_branch_order[order]
            total_radius = 0
            for node in nodes:
                total_radius += node['radius']
            avg_radius.append(total_radius / len(nodes))

        if len(orders) > 1:
            if slope_linear_regression_branch_order_avg_radius(orders, avg_radius) >= 0:
                result.append(ve("Radius should have a negative slope for the following type: %s" % dendrite, [],
                                 "Warning"))

    return result


def slope_linear_regression_branch_order_avg_radius(orders, avg_radius):

    """ Use linear regression to find the slope of the best fit line """

    m = 0

    if len(avg_radius) != 0:
        x = np.array(orders)
        y = np.array(avg_radius)

        a = np.vstack([x, np.ones(len(x))]).T
        m, c = np.linalg.lstsq(a, y, rcond=None)[0]

    return m


def validate_constrictions(morphology):

    """ This function checks if the radius of basal dendrite and apical dendrite
        nodes is smaller than their immediate child if the radius of the parent node
        is smaller 2.0px """

    result = []

    depth = []
    to_visit = [morphology.get_root()]
    while to_visit:
        node = to_visit.pop()
        if morphology.parent_of(node):
            parent_node_depth = [item[1] for item in depth if item[0] is morphology.parent_of(node)]
            depth.append((node, parent_node_depth[0] + 1))
        else:
            depth.append((node, 0))
        to_visit.extend(morphology.children_of(node))

    eligible_nodes = sorted([item[0] for item in depth if item[1] < 10])
    for node in eligible_nodes:
        if node['type'] in [BASAL_DENDRITE, APICAL_DENDRITE]:
            if node['radius'] < 2.0:
                result.append(ve("Constriction: The radius of types 3 and 4 should not be less than 2.0px", node['id'],
                                 "Warning"))

    return result


def validate(morphology):

    result = []

    result += validate_node_type_radius(morphology)

    result += validate_constrictions(morphology)

    result += validate_extreme_taper(morphology)

    result += validate_radius_has_negative_slope_dendrite(morphology, BASAL_DENDRITE)

    result += validate_radius_has_negative_slope_dendrite(morphology, APICAL_DENDRITE)

    return result
