import unittest

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.constants import (
    SOMA, AXON, APICAL_DENDRITE, BASAL_DENDRITE)


class TestMorphologyBuilder(unittest.TestCase):

    def test_branching(self):

        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .axon(0, 0, 1)
                        .axon(0, 0, 2)
                            .axon(0, 0, 3).up()
                            .axon(0, 0, 4)
                                .axon(0, 0, 5).up()
                                .axon(0, 0, 6).up(4)
                    .basal_dendrite()
                        .basal_dendrite()
                .build()
        )

        obtained = morphology.get_branching_nodes()
        self.assertEqual(obtained[0]["z"], 2)
        self.assertEqual(obtained[1]["z"], 4)
        self.assertEqual(len(obtained), 2)

    def test_multiroot(self):
        morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .axon(0, 0, 1)
                .root(1, 1, 1, AXON)
                    .child(2, 1, 1, AXON)
                .build()
        )

        roots = morphology.get_roots()
        self.assertEqual(roots[1]["parent"], -1)
        self.assertEqual(morphology.nodes()[-1]["parent"], 2)