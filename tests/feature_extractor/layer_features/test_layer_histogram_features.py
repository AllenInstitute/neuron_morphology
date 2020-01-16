import unittest

import numpy as np

import neuron_morphology.features.layer.layer_histogram as layer
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.features.layer.reference_layer_depths import \
    ReferenceLayerDepths
from neuron_morphology.features.layer.layered_point_depths import \
    LayeredPointDepths
from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.constants import AXON, APICAL_DENDRITE

            
            
def data():
            
    """
    S > A > A > A
    v
    P > P > P
        v
        P
    """
    morphology = (
        MorphologyBuilder()
            .root()
                .axon()
                    .axon()
                        .axon().up(3)
                .apical_dendrite()
                    .apical_dendrite()
                        .apical_dendrite().up()
                        .apical_dendrite()
            .build()
    )


    reference_depths = {
        "1": ReferenceLayerDepths(0, 100),
        "2": ReferenceLayerDepths(100, 200),
        "wm": ReferenceLayerDepths(200, 300, False)
    }

    # in this example specimen, layer transitions are universally at 
    # 50 250 350
    point_depths = LayeredPointDepths(
        ids=np.arange(8),
        layer_name=["2", "2", "wm", "wm", "2", "1", "1", "1"],
        depth=[200, 230, 260, 290, 60, 40, 30, 20],
        local_layer_pia_side_depth=[50, 50, 250, 250, 50, 0, 0, 0],
        local_layer_wm_side_depth=[250, 250, np.nan, np.nan, 250, 50, 50, 50],
        point_type=[node["type"] for node in morphology.nodes()]
    )

    return morphology, reference_depths, point_depths


class TestLayerHistogramFeatures(unittest.TestCase):
    
    def setUp(self):
        self.morphology, self.reference_depths, self.point_depths = data()

    def test_normalized_depth_histogram_within_layer(self):
        expected = layer.LayerHistogram( # specimen thickness half reference
            counts=np.array([0, 0, 0, 0, 1, 0, 1, 0, 1, 0]),
            bin_edges=np.arange(0, 110, 10)
        )

        depths = self.point_depths.df[self.point_depths.df["layer_name"] == "1"]

        obtained = layer.normalized_depth_histogram_within_layer(
            point_depths=depths.depth,
            local_layer_pia_side_depths=depths.local_layer_pia_side_depth,
            local_layer_wm_side_depths=depths.local_layer_wm_side_depth,
            reference_layer_depths=self.reference_depths["1"],
            bin_size=10
        )

        assert np.allclose(expected.counts, obtained.counts)
        assert np.allclose(expected.bin_edges, obtained.bin_edges)

    def test_normalized_depth_histograms_across_layers(self):

        _data = Data(
            self.morphology, 
            reference_layer_depths=self.reference_depths,
            layered_point_depths=self.point_depths
        )

        obtained = layer.normalized_depth_histogram(
            _data, bin_size=10
        )

        expected = {
            "1": layer.LayerHistogram(
                counts=np.array([0, 0, 0, 0, 1, 0, 1, 0, 1, 0]), 
                bin_edges=np.arange(0, 110, 10)),
            "2": layer.LayerHistogram(
                counts=np.array([1, 0, 0, 0, 0, 0, 0, 1, 0, 1]), 
                bin_edges=np.arange(100, 210, 10)),
            "wm": layer.LayerHistogram(
                counts=np.array([0, 1, 0, 0, 1, 0, 0, 0, 0, 0]), 
                bin_edges=np.arange(200, 310, 10))
        }

        self.assertEqual(set(expected.keys()), set(obtained.keys()))
        for key, obt in obtained.items():
            expt = expected[key]
            print(key, expt.counts, obt.counts)
            assert np.allclose(expt.counts, obt.counts)
            assert np.allclose(expt.bin_edges, obt.bin_edges)


    def test_histogram_earth_movers_distance(self):
        
        obtained = layer.histogram_earth_movers_distance(
            np.array([0, 0, 0, 1, 1, 0, 0, 0]),
            np.array([0, 0, 0, 0, 0, 0, 1, 1])
        )

        self.assertAlmostEqual(obtained.result, 3)
        self.assertEqual(
            obtained.interpretation, 
            layer.EarthMoversDistanceInterpretation.BothPresent
        )

    def test_histogram_earth_movers_distance_one_zero(self):
        obtained = layer.histogram_earth_movers_distance(
            np.array([0, 0, 0, 1, 1, 0, 0, 0]),
            np.array([0, 0, 0, 0, 0, 0, 0, 0])
        )

        self.assertEqual(obtained.result, 2)
        self.assertEqual(
            obtained.interpretation, 
            layer.EarthMoversDistanceInterpretation.OneEmpty
        )

    def test_histogram_earth_movers_distance_both_zero(self):
        obtained = layer.histogram_earth_movers_distance(
            np.array([0, 0, 0, 0, 0, 0, 0, 0]),
            np.array([0, 0, 0, 0, 0, 0, 0, 0])
        )

        self.assertEqual(obtained.result, 0)
        self.assertEqual(
            obtained.interpretation, 
            layer.EarthMoversDistanceInterpretation.BothEmpty
        )

    def test_earth_movers_distance(self):

        _data = Data(
            self.morphology, 
            reference_layer_depths=self.reference_depths,
            layered_point_depths=self.point_depths
        )

        obtained = layer.earth_movers_distance(
            _data, [AXON], [APICAL_DENDRITE]
        )

        self.assertEqual(set(obtained.keys()), {"2"})
        self.assertEqual(obtained["2"].result, 17)
