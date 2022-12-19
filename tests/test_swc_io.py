import unittest
import os
import shutil
import tempfile

from neuron_morphology.morphology_builder import MorphologyBuilder
import neuron_morphology.swc_io as swcio


class TestSWCIO(unittest.TestCase):

    def setUp(self):
        data_dir = os.path.join(os.path.dirname(__file__), 'data')
        self.swc_file = os.path.join(data_dir, 'test_swc.swc')

        self.test_dir = tempfile.mkdtemp()
        self.morphology = (
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

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_create_morphology_from_swc(self):
        morph = swcio.morphology_from_swc(self.swc_file)
        self.assertEqual(morph.get_root()['parent'], -1)
        self.assertEqual(morph.node_by_id(2)['parent'], 1)

    def test_save_morphology_to_swc(self):
        test_swc_path = os.path.join(self.test_dir, 'test.swc')
        swcio.morphology_to_swc(self.morphology, test_swc_path)

        with open(test_swc_path, 'r') as test_swc:
            line = test_swc.readline().rstrip().split(' ')
            self.assertEqual(int(line[-1]), -1)
            line = test_swc.readline().rstrip().split(' ')
            self.assertEqual(float(line[-1]), 0.0)
