import unittest

import math
from neuron_morphology.features import soma
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE)
from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.feature_extractor.feature_extractor import (
    FeatureExtractor
)
from neuron_morphology.feature_extractor.marked_feature import (
    specialize
)
from neuron_morphology.feature_extractor.feature_specialization import (
    BasalDendriteSpec, AxonSpec
)



def basic_nodes():
    """
    This morphology looks like:
    S -10-> A -10-> A
    |
    3-> AD -3-> AD
    """
    return [
        {
            "id": 0,
            "parent_id": -1,
            "type": SOMA,
            "x": 0,
            "y": 0,
            "z": 100,
            "radius": 5
        },
        {
            "id": 1,
            "parent_id": -1,
            "type": AXON,
            "x": 1,
            "y": 5,
            "z": 110,
            "radius": 1
        },
        {
            "id": 2,
            "parent_id": 1,
            "type": AXON,
            "x": 3,
            "y": 10,
            "z": 120,
            "radius": 1
        },
        {
            "id": 3,
            "parent_id": 0,
            "type": APICAL_DENDRITE,
            "x": 5,
            "y": 15,
            "z": 100,
            "radius": 1
        },
        {
            "id": 4,
            "parent_id": 3,
            "type": APICAL_DENDRITE,
            "x": 7,
            "y": 20,
            "z": 100,
            "radius": 1
        },
    ]


class MorphSomaTest(unittest.TestCase):
    def setUp(self):
        self.morphology = Morphology(
            basic_nodes(),
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )
        self.data = Data(self.morphology, relative_soma_depth= 0.25)

class TestSomaFeatures(MorphSomaTest):
    
    def test_soma_surface(self):
        obtained = soma.calculate_soma_surface(self.data)
        self.assertAlmostEqual(obtained, 4.0 * math.pi * 5 * 5)

    def test_relative_soma_depth(self):
        obtained = soma.calculate_relative_soma_depth(self.data)
        self.assertAlmostEqual(obtained, 0.25)

    def test_stem_exit_and_distance(self):
        first, second = soma.calculate_stem_exit_and_distance(self.data, [AXON])[0]
        self.assertAlmostEqual(first, 0.447, 3)
        self.assertAlmostEqual(second, 11.22, 2)

    def test_stem_exit_with_type(self):

        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0, radius=10)
                    .basal_dendrite(10, 0, 0, radius=2)
                        .basal_dendrite(20, 0, 0, radius=2).up()
                        .axon(30, 0, 0, radius=0.5)
                            .axon(40, 0, 0, radius=0.5).up(3)
                    .basal_dendrite(0, -10, 0, radius=2)
                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(soma.calculate_stem_exit_and_distance, [BasalDendriteSpec, AxonSpec])])
        feature_extraction_run = fe.extract(cell_data)

        axon_results = feature_extraction_run.results["axon.calculate_stem_exit_and_distance"]
        basal_results = feature_extraction_run.results["basal_dendrite.calculate_stem_exit_and_distance"]
        self.assertEqual(axon_results[0][0], 0.5)
        self.assertEqual(axon_results[0][1], 30.0)
        self.assertEqual(basal_results[0][0], 0.5)
        self.assertEqual(basal_results[0][1], 0)
        self.assertEqual(basal_results[1][0], 1)
        self.assertEqual(basal_results[1][1], 0)

    def test_number_of_stems_with_type(self):

        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .axon().up()
                    .basal_dendrite().up()
                    .basal_dendrite()
                .build()
        )

        cell_data = Data(morphology=morphology)
        fe = FeatureExtractor()
        fe.register_features([specialize(soma.calculate_number_of_stems, [BasalDendriteSpec])])
        feature_extraction_run = fe.extract(cell_data)

        self.assertEqual(
            feature_extraction_run.results["basal_dendrite.calculate_number_of_stems"],
            2
        )





class TestSomaPercentile(unittest.TestCase):
    def setUp(self):
        # morphology with 3/4 axons below soma in z
        self.morphology = Morphology([
            {
                "id": 0,
                "parent_id": -1,
                "type": SOMA,
                "x": 0,
                "y": 0,
                "z": 100,
                "radius": 5
            },
            {
                "id": 1,
                "parent_id": 0,
                "type": AXON,
                "x": 0,
                "y": 0,
                "z": 110,
                "radius": 1
            },
            {
                "id": 2,
                "parent_id": 1,
                "type": AXON,
                "x": 0,
                "y": 0,
                "z": 90,
                "radius": 1
            },
            {
                "id": 3,
                "parent_id": 2,
                "type": AXON,
                "x": 0,
                "y": 0,
                "z": 80,
                "radius": 1
            },
            {
                "id": 4,
                "parent_id": 3,
                "type": AXON,
                "x": 0,
                "y": 0,
                "z": 70,
                "radius": 1
            },
        ],
            node_id_cb=lambda node: node["id"],
            parent_id_cb=lambda node: node["parent_id"],
        )

        self.data = Data(self.morphology)

    def test_soma_percentile(self):
        obtained = soma.soma_percentile(self.data, [AXON])
        self.assertEqual(obtained[2], 0.25)

    def test_soma_percentile_no_sym(self):
        obtained = soma.soma_percentile(self.data, [AXON], symmetrize_xz=False)
        self.assertEqual(obtained[2], 0.75)
