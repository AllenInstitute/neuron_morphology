import collections
import numpy as np
from neuron_morphology.validation.result import NodeValidationError as ve
from neuron_morphology.constants import *


def validate_radius_threshold(morphology):

    """ This function validates the radius for types 1, 3, and 4 """

    result = []

    soma_radius_threshold = 35
    dendrite_radius_threshold = 20

    soma = morphology.get_root()
    if soma['radius'] < soma_radius_threshold:
        result.append(ve("The radius must be above %spx for type 1" % soma_radius_threshold, soma['id'], "Info"))

    dendrite_nodes = morphology.get_node_by_types([BASAL_DENDRITE, APICAL_DENDRITE])

    for node in dendrite_nodes:
        if node['radius'] > dendrite_radius_threshold:
            result.append(ve("The radius must be below %spx for types 3 and 4" % dendrite_radius_threshold,
                             node['id'], "Info"))

    return result


def validate_extreme_taper(morphology):

    """ This function checks whether there is an extreme taper.
        Extreme taper occurs when for each segment, the average
        radius of the first two nodes is more than two times the
        average radius of the last two nodes.

         Note: This tests is limited to segments of at lease 8 nodes. """

    result = []

    for segment in morphology.get_segment_list():
        if len(segment) > 7:
            if segment[0]['type'] in [BASAL_DENDRITE, APICAL_DENDRITE]:
                average_radius_beginning = (segment[0]['radius'] + segment[1]['radius'])/2
                average_radius_end = (segment[-1]['radius'] + segment[-2]['radius'])/2
                if average_radius_beginning > 4 * average_radius_end:
                    result.append(ve("Extreme Taper: For types 3 and 4, the average radius of the first two nodes "
                                     "in a segment should not be greater than four times the average radius of the "
                                     "last two nodes in a segment (For segments that have more than 8 nodes)",
                                     [segment[0]['id'], segment[-2]['id']], "Info"))

    return result


def validate_radius_has_negative_slope_dendrite(morphology, dendrite):

    """ This function checks whether the radius for dendrite nodes decreases
        when you are going away from the soma. """

    result = []

    root = (morphology.get_root())
    if root['type'] is not SOMA:
        return result

    nodes_by_branch_order = collections.defaultdict(list)

    root_children = morphology.get_children_of_node_by_types(root, [dendrite])
    to_visit = [(child, 1) for child in root_children]

    while to_visit:
        (node, parent_order) = to_visit.pop()
        children = morphology.get_children_of_node_by_types(node, [dendrite])

        if len(children) > 1:
            order = parent_order + 1
        else:
            order = parent_order

        nodes_by_branch_order[order].append(node)
        to_visit.extend([(child_node, order)
                         for child_node in children])

    orders = sorted(nodes_by_branch_order.keys())
    avg_radius = []

    for order in orders:
        nodes = nodes_by_branch_order[order]
        total_radius = 0
        for node in nodes:
            total_radius += node['radius']
        avg_radius.append(total_radius / len(nodes))

    if len(orders) > 1:
        if slope_linear_regression_branch_order_avg_radius(orders,
                                                           avg_radius) >= 0:
            result.append(ve("Radius should have a negative slope for the "
                             "following type: %s" % dendrite, [],
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
        nodes is smaller 2.0px """

    result = []

    # start with root, do depth-first traverse up to depth 10
    eligible_nodes = []
    to_visit = [(morphology.get_root(), 0)]

    while to_visit:
        (node, depth) = to_visit.pop()
        if depth < 10:
            eligible_nodes.append(node)
            to_visit.extend([(child_node, depth + 1)
                             for child_node in morphology.children_of(node)])

    for node in eligible_nodes:
        if node['type'] in [BASAL_DENDRITE, APICAL_DENDRITE]:
            if node['radius'] < 2.0:
                result.append(ve("Constriction: The radius of types 3 and 4 "
                                 "should not be less than 2.0px",
                                 node['id'],
                                 "Warning"))

    return result


def validate(morphology):

    result = []

    result += validate_radius_threshold(morphology)

    result += validate_constrictions(morphology)

    result += validate_extreme_taper(morphology)

    result += validate_radius_has_negative_slope_dendrite(morphology, BASAL_DENDRITE)

    result += validate_radius_has_negative_slope_dendrite(morphology, APICAL_DENDRITE)

    return result
