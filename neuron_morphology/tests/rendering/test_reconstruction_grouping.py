import unittest
from neuron_morphology.rendering.reconstruction_grouping import sort_reconstructions, \
    create_reconstruction_grouping


class TestReconstructionGrouping(unittest.TestCase):
    def test_create_reconstruction_grouping(self):
        reconstruction_hierarchy = [{'attribute': 'layer', 'sort': 'desc'}]
        reconstruction_card_properties = [{'attribute': 'structure', 'sort': 'asc'}]
        reconstructions = [{'layer': '1', 'structure': 'a'}, {'layer': '2', 'structure': 'b'}]
        reconstruction_grouping = create_reconstruction_grouping(reconstruction_hierarchy,
                                                                 reconstruction_card_properties,
                                                                 reconstructions)
        reconstruction_grouping.__repr__()
        self.assertEqual(list(reconstruction_grouping.sub_groups.keys()), ['2', '1'])
        self.assertEqual(reconstruction_grouping.sub_groups['2'].ungrouped_reconstructions, [reconstructions[1]])
        self.assertEqual(reconstruction_grouping.sub_groups['1'].ungrouped_reconstructions, [reconstructions[0]])

    def test_sort_reconstructions(self):
        reconstructions = [{'dendrite_tag': '1', 'apical_tag': 'a'}, {'dendrite_tag': '2', 'apical_tag': 'b'},
                           {'dendrite_tag': '1', 'apical_tag': 'b'}, {'dendrite_tag': '2', 'apical_tag': 'a'}]
        reconstruction_card_properties = [{'attribute': 'dendrite_tag', 'sort': 'asc'},
                                          {'attribute': 'apical_tag', 'sort': 'desc'}]
        sorted_reconstructions = sort_reconstructions(reconstruction_card_properties, reconstructions)
        self.assertEqual([{'dendrite_tag': '1', 'apical_tag': 'b'}, {'dendrite_tag': '1', 'apical_tag': 'a'},
                          {'dendrite_tag': '2', 'apical_tag': 'b'}, {'dendrite_tag': '2', 'apical_tag': 'a'}],
                         sorted_reconstructions)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestReconstructionGrouping)
    unittest.TextTestRunner(verbosity=5).run(suite)
