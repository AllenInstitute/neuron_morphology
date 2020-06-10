import unittest

import neuron_morphology.features.path as path
from neuron_morphology.morphology import Morphology
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)
from neuron_morphology.feature_extractor.feature_extractor import (
    FeatureExtractor
)
from neuron_morphology.feature_extractor.feature_specialization import (
    NEURITE_SPECIALIZATIONS)
from neuron_morphology.feature_extractor.marked_feature import specialize
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.morphology_builder import MorphologyBuilder

class PathTestCase(unittest.TestCase):
    def setUp(self):
        self.morphology = Morphology([
                {
                    "id": 0,
                    "parent_id": -1,
                    "type": SOMA,
                    "x": 0,
                    "y": 0,
                    "z": 100,
                    "radius": 1
                },
                {
                    "id": 1,
                    "parent_id": 0,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 101,
                    "radius": 1
                },
                {
                    "id": 2,
                    "parent_id": 0,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 102,
                    "radius": 1
                },
                { # bifurcates
                    "id": 3,
                    "parent_id": 1,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 110,
                    "radius": 1
                },                
                {
                    "id": 4,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 140,
                    "radius": 1 
                },     
                { # this node backtracks, causing the path distance to differ from the euclidean
                    "id": 11,
                    "parent_id": 4,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 130,
                    "radius": 1 
                },       
                { # bifurcates
                    "id": 5,
                    "parent_id": 3,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 130,
                    "radius": 1 
                },                
                {
                    "id": 6,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 0,
                    "y": 0,
                    "z": 135,
                    "radius": 1 
                },       
                {
                    "id": 7,
                    "parent_id": 5,
                    "type": AXON,
                    "x": 30,
                    "y": 0,
                    "z": 103,
                    "radius": 1 
                },     
                { # bifurcates
                    "id": 8,
                    "parent_id": 2,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 125,
                    "radius": 1 
                },
                {
                    "id": 9,
                    "parent_id": 8,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 126,
                    "radius": 1 
                },
                {
                    "id": 10,
                    "parent_id": 8,
                    "type": APICAL_DENDRITE,
                    "x": 0,
                    "y": 0,
                    "z": 127,
                    "radius": 1 
                },
            ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )


class TestMeanContraction(PathTestCase):

    def test_generic(self):
        self.assertAlmostEqual(
            path.mean_contraction(self.morphology),
            0.86049192013635
        )

    def test_specific(self):
        self.assertAlmostEqual(
            path.mean_contraction(
                self.morphology, node_types=[APICAL_DENDRITE]),
            1.0 # only axons backtrack
        )

    def test_specialized(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .basal_dendrite(1, 0, 0)
                        .basal_dendrite(2, 0, 0)
                            .basal_dendrite(2, 1, 0)
                                .basal_dendrite(1, 1, 0).up()
                                .basal_dendrite(3, 1, 0).up(2)
                            .axon(2, -1, 0)
                                .axon(2, -2, 0)
                                    .axon(1, -2, 0).up()
                                    .axon(3, -2, 0).up(5)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                            .apical_dendrite(-1, 2, 0).up()
                            .apical_dendrite(1, 2, 0)
                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(path.mean_contraction, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["axon.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["dendrite.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.mean_contraction"], 1)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.mean_contraction"], 1)


class TestEarlyBranchPath(PathTestCase):

    def test_generic(self):

        self.assertAlmostEqual(
            path.early_branch_path(self.morphology),
            40 / 70.36087214122114 
            # longest short path distance is 40 on the path starting 3 -> 4
            # 70. ...  is the max_path_distance of this tree
        )


class TestMaxPathDistance(PathTestCase):

    def test_generic(self):
        self.assertAlmostEqual(
            path.max_path_distance(self.morphology),
            70.36087214122114
        )

    def test_specialized(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .basal_dendrite(1, 0, 0)
                        .axon(1, -1, 0).up()
                        .basal_dendrite(2, 0, 0)
                            .basal_dendrite(3, 0, 0).up()
                            .basal_dendrite(2, 1, 0).up(3)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                            .apical_dendrite(-1, 2, 0).up()
                            .apical_dendrite(1, 2, 0)
                                .apical_dendrite(1, 3, 0)
                .build()
        )


        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(path.max_path_distance, NEURITE_SPECIALIZATIONS)])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(feature_extraction_run.results["all_neurites.max_path_distance"], 4)
        self.assertEqual(feature_extraction_run.results["axon.max_path_distance"], 2)
        self.assertEqual(feature_extraction_run.results["dendrite.max_path_distance"], 4)
        self.assertEqual(feature_extraction_run.results["basal_dendrite.max_path_distance"], 3)
        self.assertEqual(feature_extraction_run.results["apical_dendrite.max_path_distance"], 4)
