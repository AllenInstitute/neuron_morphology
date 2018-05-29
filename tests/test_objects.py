from allensdk.neuron_morphology.morphology import Morphology
from allensdk.neuron_morphology.tree import Tree
from allensdk.neuron_morphology.marker import Marker
from allensdk.neuron_morphology.constants import *
from allensdk.neuron_morphology.rendering.morphology_summary import MorphologySummary
from allensdk.neuron_morphology.rendering.density_graph import CorticalDepthHistogram
from allensdk.neuron_morphology.rendering.density_graph import DensityGraph

test_pia_transform = {

    "id": 611512262,
    "tvr_00": -0.984586262715884,
    "tvr_01": 0.174899660580482,
    "tvr_02": 0.0,
    "tvr_03": -0.174899660580482,
    "tvr_04": -0.984586262715884,
    "tvr_05": 0.0,
    "tvr_06": 0.0,
    "tvr_07": 0.0,
    "tvr_08": 1.0,
    "tvr_09": 1095.28453097201,
    "tvr_10": 368.33610557072,
    "tvr_11": -31.08,
    "trv_00": -0.984586262715884,
    "trv_01": -0.174899660580482,
    "trv_02": 0.0,
    "trv_03": 0.174899660580482,
    "trv_04": -0.984586262715884,
    "trv_05": 0.0,
    "trv_06": 0.0,
    "trv_07": 0.0,
    "trv_08": 1.0,
    "trv_09": 1142.82396280411,
    "trv_10": 171.093776901141,
    "trv_11": 31.08,
    "metric": None,
    "scale_x": 1.0,
    "scale_y": 1.0,
    "scale_z": 1.0,
    "rotation_x": -3.31739651059373,
    "rotation_y": -3.31739651059373,
    "rotation_z": 0.0,
    "skew_x": 0.0,
    "skew_y": 0.0,
    "skew_z": 0.0,
    "created_at": "2017-08-21 14:47:44 -0700",
    "updated_at": "2017-08-21 14:47:44 -0700"

}

test_soma_depth = 446.340044904363
test_relative_soma_depth = 0.142356042101816


def test_node(id=1, type=SOMA, x=0.0, y=0.0, z=0.0, radius=1, parent_node_id=-1):
    return {'id': id, 'type': type, 'x': x, 'y': y, 'z': z, 'radius': radius, 'parent': parent_node_id}


def test_marker(x=0.0, y=0.0, z=0.0, name=NO_RECONSTRUCTION):
    return Marker({'x': x, 'y': y, 'z': z, 'name': name})


def test_tree(nodes, strict_validation=False):

    for node in nodes:
        # unfortunately, pandas automatically promotes numeric types to float in to_dict
        node['parent'] = int(node['parent'])
        node['id'] = int(node['id'])
        node['type'] = int(node['type'])

    node_id_cb = lambda node: node['id']
    parent_id_cb = lambda node: node['parent']

    return Tree(nodes, node_id_cb, parent_id_cb, strict_validation)


def test_morphology_large():

    nodes = [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
             test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
             test_node(id=3, type=BASAL_DENDRITE, x=430, y=630, z=20, radius=3, parent_node_id=2),
             test_node(id=4, type=BASAL_DENDRITE, x=460, y=660, z=30, radius=3, parent_node_id=3),
             test_node(id=5, type=BASAL_DENDRITE, x=490, y=690, z=40, radius=3, parent_node_id=4),
             test_node(id=6, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
             test_node(id=7, type=APICAL_DENDRITE, x=630, y=330, z=30, radius=3, parent_node_id=6),
             test_node(id=8, type=APICAL_DENDRITE, x=660, y=360, z=40, radius=3, parent_node_id=7),
             test_node(id=9, type=APICAL_DENDRITE, x=690, y=390, z=50, radius=3, parent_node_id=8),
             test_node(id=10, type=APICAL_DENDRITE, x=710, y=420, z=60, radius=3, parent_node_id=9),
             test_node(id=11, type=APICAL_DENDRITE, x=740, y=450, z=70, radius=3, parent_node_id=10),
             test_node(id=12, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1),
             test_node(id=13, type=AXON, x=930, y=630, z=40, radius=3, parent_node_id=12),
             test_node(id=14, type=AXON, x=960, y=660, z=50, radius=3, parent_node_id=13),
             test_node(id=15, type=AXON, x=990, y=690, z=60, radius=3, parent_node_id=14),
             test_node(id=16, type=AXON, x=1020, y=720, z=70, radius=3, parent_node_id=15),
             test_node(id=17, type=AXON, x=1050, y=750, z=80, radius=3, parent_node_id=16)]

    for node in nodes:
        # unfortunately, pandas automatically promotes numeric types to float in to_dict
        node['parent'] = int(node['parent'])
        node['id'] = int(node['id'])
        node['type'] = int(node['type'])

    return Tree(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'],
                strict_validation=True)


def test_morphology_small():

    nodes = [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
             test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
             test_node(id=3, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
             test_node(id=4, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1)]

    for node in nodes:
        # unfortunately, pandas automatically promotes numeric types to float in to_dict
        node['parent'] = int(node['parent'])
        node['id'] = int(node['id'])
        node['type'] = int(node['type'])

    return Tree(nodes, node_id_cb=lambda node: node['id'], parent_id_cb=lambda node: node['parent'],
                strict_validation=True)


def test_morphology_summary(morphology=test_morphology_small(), pia_transform=test_pia_transform, width=0, height=0,
                            ordered_node_types=None):
    if ordered_node_types is None:
        ordered_node_types = [AXON, BASAL_DENDRITE, APICAL_DENDRITE, SOMA]
    return MorphologySummary(morphology, pia_transform, width, height, ordered_node_types)


def test_cortical_depth_histogram(number_of_bins=10, soma_depth=test_soma_depth,
                                  relative_soma_depth=test_relative_soma_depth):
    return CorticalDepthHistogram(number_of_bins, soma_depth, relative_soma_depth)


def test_density_graph(morphology=test_morphology_small(), width=100, height=100, soma_depth=test_soma_depth
                       , relative_soma_depth=test_relative_soma_depth, ordered_node_types=None):
    if ordered_node_types is None:
        ordered_node_types = [AXON, BASAL_DENDRITE, APICAL_DENDRITE, SOMA]
    return DensityGraph(morphology, width, height, soma_depth, relative_soma_depth, ordered_node_types)
