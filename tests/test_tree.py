import unittest
from neuron_morphology.constants import *
from neuron_morphology.morphology import Morphology
from tests.objects import (test_node,
                           test_morphology_small,
                           test_morphology_small_branching,
                           test_morphology_small_multiple_trees,
                           test_morphology_large,
                           )


class TestTree(unittest.TestCase):

    def test_get_root(self):

        morphology = test_morphology_small()
        expected_root = test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1)
        self.assertEqual(expected_root, morphology.get_root())

    def test_len(self):

        morphology = test_morphology_small()
        expected_length = 7
        self.assertEqual(expected_length, len(morphology))

    def test_children_of(self):

        morphology = test_morphology_small()
        node = test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1)
        children = morphology.children_of(node)
        expected_children = [test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
                             test_node(id=4, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
                             test_node(id=6, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1)]
        self.assertEqual(children, expected_children)

    def test_parent_of(self):

        morphology = test_morphology_small()
        node = test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)
        expected_parent = test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1)
        parent = morphology.parent_of(node)
        self.assertEqual(expected_parent, parent)

    def test_get_children_of_node_by_type(self):

        morphology = test_morphology_small()
        node = test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1)
        expected_children_by_type = {BASAL_DENDRITE: [test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)],
                                     APICAL_DENDRITE: [test_node(id=4, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1)],
                                     AXON: [test_node(id=6, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1)]}
        for node_type in [BASAL_DENDRITE, APICAL_DENDRITE, AXON]:
            child = morphology.get_children_of_node_by_types(node, [node_type])
            self.assertEqual(expected_children_by_type[node_type], child)

    def test_node_by_id(self):

        morphology = test_morphology_small()
        expected_node = test_node(id=4, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1)
        node_by_id = morphology.node_by_id(4)
        self.assertEqual(expected_node, node_by_id)

    def test_get_root_id(self):

        morphology = test_morphology_small()
        expected_root_id = 1
        root_id = morphology.get_root_id()
        self.assertEqual(expected_root_id, root_id)

    def test_get_number_of_trees(self):

        morphology = test_morphology_small_multiple_trees()
        expected_number_of_trees = 2
        number_of_trees = morphology.get_number_of_trees()
        self.assertEqual(expected_number_of_trees, number_of_trees)

    def test_get_tree_list(self):

        morphology = test_morphology_small_multiple_trees()
        expected_trees = [[test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                           test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
                           test_node(id=3, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
                           test_node(id=4, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1)
                           ],
                          [test_node(id=5, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=-1),
                           test_node(id=6, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=5),
                           test_node(id=7, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=6),
                           test_node(id=8, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=7),
                           test_node(id=9, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=8)
                           ]]
        trees = morphology.get_tree_list()
        self.assertEqual(expected_trees, trees)

    def test_get_tree_root(self):

        morphology = test_morphology_small_multiple_trees()
        root_by_number = {0: test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                          1: test_node(id=5, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=-1)}
        for tree_number in [0, 1]:
            root = morphology.get_root_for_tree(tree_number)
            self.assertEqual(root_by_number[tree_number], root)

    def test_get_node_by_types_basal(self):

        morphology = test_morphology_large()
        expected_nodes = [test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
                          test_node(id=3, type=BASAL_DENDRITE, x=430, y=630, z=20, radius=3, parent_node_id=2),
                          test_node(id=4, type=BASAL_DENDRITE, x=460, y=660, z=30, radius=3, parent_node_id=3),
                          test_node(id=5, type=BASAL_DENDRITE, x=490, y=690, z=40, radius=3, parent_node_id=4)]

        nodes = morphology.get_node_by_types([BASAL_DENDRITE])
        self.assertEqual(expected_nodes, nodes)

    def test_get_node_by_types_apical(self):

        morphology = test_morphology_large()
        expected_nodes = [test_node(id=6, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
                          test_node(id=7, type=APICAL_DENDRITE, x=630, y=330, z=30, radius=3, parent_node_id=6),
                          test_node(id=8, type=APICAL_DENDRITE, x=660, y=360, z=40, radius=3, parent_node_id=7),
                          test_node(id=9, type=APICAL_DENDRITE, x=690, y=390, z=50, radius=3, parent_node_id=8),
                          test_node(id=10, type=APICAL_DENDRITE, x=710, y=420, z=60, radius=3, parent_node_id=9),
                          test_node(id=11, type=APICAL_DENDRITE, x=740, y=450, z=70, radius=3, parent_node_id=10)]

        nodes = morphology.get_node_by_types([APICAL_DENDRITE])
        self.assertEqual(expected_nodes, nodes)

    def test_get_node_by_types_axon(self):

        morphology = test_morphology_large()
        expected_nodes = [test_node(id=12, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1),
                          test_node(id=13, type=AXON, x=930, y=630, z=40, radius=3, parent_node_id=12),
                          test_node(id=14, type=AXON, x=960, y=660, z=50, radius=3, parent_node_id=13),
                          test_node(id=15, type=AXON, x=990, y=690, z=60, radius=3, parent_node_id=14),
                          test_node(id=16, type=AXON, x=1020, y=720, z=70, radius=3, parent_node_id=15),
                          test_node(id=17, type=AXON, x=1050, y=750, z=80, radius=3, parent_node_id=16)]

        nodes = morphology.get_node_by_types([AXON])
        self.assertEqual(expected_nodes, nodes)

    def test_get_non_soma_nodes(self):

        morphology = test_morphology_small()
        expected_nodes = [test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
                          test_node(id=3, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=2),
                          test_node(id=4, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
                          test_node(id=5, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=4),
                          test_node(id=6, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1),
                          test_node(id=7, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=6)]

        nodes = morphology.get_non_soma_nodes()
        self.assertEqual(expected_nodes, nodes)

    def test_get_max_id(self):

        morphology = test_morphology_large()
        expected_id = 17
        max_id = morphology.get_max_id()
        self.assertEqual(expected_id, max_id)

    def test_get_segment_list(self):

        morphology = test_morphology_large()
        segments = morphology.get_segment_list()
        expected_segments = [[test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
                              test_node(id=3, type=BASAL_DENDRITE, x=430, y=630, z=20, radius=3, parent_node_id=2),
                              test_node(id=4, type=BASAL_DENDRITE, x=460, y=660, z=30, radius=3, parent_node_id=3),
                              test_node(id=5, type=BASAL_DENDRITE, x=490, y=690, z=40, radius=3, parent_node_id=4)],
                             [test_node(id=6, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
                              test_node(id=7, type=APICAL_DENDRITE, x=630, y=330, z=30, radius=3, parent_node_id=6),
                              test_node(id=8, type=APICAL_DENDRITE, x=660, y=360, z=40, radius=3, parent_node_id=7),
                              test_node(id=9, type=APICAL_DENDRITE, x=690, y=390, z=50, radius=3, parent_node_id=8),
                              test_node(id=10, type=APICAL_DENDRITE, x=710, y=420, z=60, radius=3, parent_node_id=9),
                              test_node(id=11, type=APICAL_DENDRITE, x=740, y=450, z=70, radius=3, parent_node_id=10)],
                             [test_node(id=12, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1),
                              test_node(id=13, type=AXON, x=930, y=630, z=40, radius=3, parent_node_id=12),
                              test_node(id=14, type=AXON, x=960, y=660, z=50, radius=3, parent_node_id=13),
                              test_node(id=15, type=AXON, x=990, y=690, z=60, radius=3, parent_node_id=14),
                              test_node(id=16, type=AXON, x=1020, y=720, z=70, radius=3, parent_node_id=15),
                              test_node(id=17, type=AXON, x=1050, y=750, z=80, radius=3, parent_node_id=16)]]
        self.assertEqual(expected_segments, segments)

    def test_get_compartment_list(self):

        morphology = test_morphology_small()
        compartments = morphology.compartments
        expected_compartments = [[test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                                  test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)],
                                 [test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1),
                                  test_node(id=3, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=2)],
                                 [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                                  test_node(id=4, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1)],
                                 [test_node(id=4, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3, parent_node_id=1),
                                  test_node(id=5, type=APICAL_DENDRITE, x=600, y=300, z=20, radius=3,
                                            parent_node_id=4)],
                                 [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                                  test_node(id=6, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1)],
                                 [test_node(id=6, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=1),
                                  test_node(id=7, type=AXON, x=900, y=600, z=30, radius=3, parent_node_id=6)]]

        self.assertEqual(expected_compartments, compartments)

    def test_get_compartment_for_node(self):

        morphology = test_morphology_small()
        node = test_node(id=3, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=2)
        compartment = morphology.get_compartment_for_node(node)
        expected_compartment = [test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1), node]
        self.assertEqual(expected_compartment, compartment)

    def test_get_compartment_for_node_with_type(self):

        morphology = test_morphology_small()
        node_types = [AXON]
        node = test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)
        compartment = morphology.get_compartment_for_node(node, node_types)
        expected_compartment = None
        self.assertEqual(expected_compartment, compartment)

    def test_get_compartment_for_node_with_no_type(self):

        morphology = test_morphology_small()
        node = test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)
        compartment = morphology.get_compartment_for_node(node)
        expected_compartment = [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1), node]
        self.assertEqual(expected_compartment, compartment)

    def test_get_compartment_length(self):

        morphology = test_morphology_small()
        compartment = [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                       test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)]
        expected_legnth = 400.6245124802026
        length = morphology.get_compartment_length(compartment)
        self.assertEqual(expected_legnth, length)


    def test_get_compartment_surface_area(self):
        morphology = test_morphology_small()  # not actually using nodes

        compartment = [
            {"x": 0, "y": 0, "z": 0, "radius": 10},
            {"x": 0, "y": 0, "z": 5, "radius": 5}
        ]

        self.assertAlmostEqual(
            morphology.get_compartment_surface_area(compartment),
            333.21622,
            places=6
        )

    def test_get_compartment_volume(self):
        morphology = test_morphology_small()  # not actually using nodes

        compartment = [
            {"x": 0, "y": 0, "z": 0, "radius": 10},
            {"x": 0, "y": 0, "z": 5, "radius": 5}
        ]

        self.assertAlmostEqual(
            morphology.get_compartment_volume(compartment),
            916.297857,
            places=6
        )

    def test_get_compartment_midpoint(self):

        morphology = test_morphology_small()
        compartment = [test_node(id=1, type=SOMA, x=800, y=610, z=30, radius=35, parent_node_id=-1),
                       test_node(id=2, type=BASAL_DENDRITE, x=400, y=600, z=10, radius=3, parent_node_id=1)]
        midpoint = morphology.get_compartment_midpoint(compartment)
        expected_midpoint = [600.0, 605.0, 20.0]
        self.assertEqual(expected_midpoint, midpoint)

    def test_get_leaf_nodes(self):

        morphology = test_morphology_small()
        leaf_nodes = morphology.get_leaf_nodes()
        expected_leaf_node_ids = set([3, 5, 7])
        self.assertEqual(set([leaf_node['id'] for leaf_node in leaf_nodes]),
                         expected_leaf_node_ids)

    def test_get_branching_nodes(self):

        morphology = test_morphology_small_branching()
        branching_nodes = morphology.get_branching_nodes()
        expected_branching_node_ids = set([3, 7, 11])
        self.assertEqual(set([branching_node['id']
                              for branching_node in branching_nodes]),
                         expected_branching_node_ids)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTree)
    unittest.TextTestRunner(verbosity=5).run(suite)
