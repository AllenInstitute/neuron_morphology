from unittest import TestCase

import numpy as np

from neuron_morphology.snap_polygons.bounding_box import BoundingBox


class TestBoundingBox(TestCase):

    def setUp(self):
        self.box = BoundingBox(10, 20, 30, 40)

    def test_update(self):
        self.box.update(20, 15, 35, 40)

        assert np.allclose(
            self.box.coordinates,
            [10, 15, 35, 40]
        )

    def test_transform(self):
        new = self.box.transform( lambda v, h: (v *2, h) )
        assert np.allclose(
            new.coordinates,
            [20, 20, 60, 40]
        )

    def test_transform_inplace(self):
        self.box.transform( lambda v, h: (v *2, h) , inplace=True)
        assert np.allclose(
            self.box.coordinates,
            [20, 20, 60, 40]
        )

    def test_copy(self):
        new = self.box.copy()
        new.vorigin = 12
        self.assertEqual(self.box.vorigin, 20)

    def test_round(self):
        box = BoundingBox(10.5, 20, 30, 40.5)
        new = box.round(origin_via=np.floor, extent_via=np.ceil)
        assert np.allclose(
            new.coordinates,
            [10, 20, 30, 41]
        )