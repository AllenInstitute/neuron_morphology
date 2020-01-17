import unittest

import numpy as np

from neuron_morphology.features.layer.reference_layer_depths import \
    ReferenceLayerDepths


class TestReferenceLayerDepths(unittest.TestCase):

    def test_thickness(self):
        depths = ReferenceLayerDepths(1, 2)
        self.assertEqual(depths.thickness, 1)

    def test_sequential(self):
        depths = ReferenceLayerDepths.sequential(["a", "b", "wm"], [1, 2, 3, 4])
        
        assert np.allclose([depth.pia_side for depth in depths.values()], 
            [1, 2, 3])
        assert np.allclose([depth.wm_side for depth in depths.values()], 
            [2, 3, 4])
        assert np.allclose([depth.scale for depth in depths.values()], 
            [True, True, False])
        self.assertEqual(set(depths.keys()), {"a", "b", "wm"})

    def test_sequential_mismatched(self):
        with self.assertRaises(AssertionError):
            ReferenceLayerDepths.sequential(["a", "b", "wm"], [1, 2, 3, 4, 5])

    def test_sequential_all_scale(self):
        depths = ReferenceLayerDepths.sequential(["a", "b", "wm"], 
            [1, 2, 3, 4], last_is_scale=True)
        assert np.allclose([depth.scale for depth in depths.values()], 
            [True, True, True])