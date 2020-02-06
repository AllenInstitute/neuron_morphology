import unittest

import numpy as np

from neuron_morphology.morphology_builder import MorphologyBuilder
from neuron_morphology.transforms.affine_transform import (
    AffineTransform, rotation_from_angle, affine_from_translation,
    affine_from_transform, affine_from_transform_translation)


class TestAffine(unittest.TestCase):

    def setUp(self):
        """
        y+
        |
        P
        ^
        P
        ^
        S > A > A - x+
        """
        self.morphology = (
            MorphologyBuilder()
                .root(0, 0, 0)
                    .axon(1, 0, 0)
                        .axon(2, 0, 0).up(2)
                    .apical_dendrite(0, 1, 0)
                        .apical_dendrite(0, 2, 0)
                .build()
            )
        self.point = [0, 1, 0]
        self.vector = [[0, 0, 0],
                       [1, 0, 0],
                       [2, 0, 0],
                       [0, 1, 0],
                       [0, 2, 0]]
        """
        [[tvr_00 tvr_01 tvr_02 tvr_09]
         [tvr_03 tvr_04 tvr_05 tvr_10]
         [tvr_06 tvr_07 tvr_08 tvr_11]
         [0      0      0      1]]
        """
        rad = 60 * np.pi / 180
        self.rad = rad
        self.array = [[np.cos(rad), -np.sin(rad), 0, 0],
                      [np.sin(rad), np.cos(rad), 0, 10],
                      [0, 0, 1, 0],
                      [0, 0, 0, 1]]

        self.translation = [0, 10, 0]
        self.list = [np.cos(rad), -np.sin(rad), 0, np.sin(rad), np.cos(rad), 0,
                     0, 0, 1, 0, 10, 0]
        self.dict = {'tvr_00': np.cos(rad),
                     'tvr_01': -np.sin(rad),
                     'tvr_02': 0,
                     'tvr_03': np.sin(rad),
                     'tvr_04': np.cos(rad),
                     'tvr_05': 0,
                     'tvr_06': 0,
                     'tvr_07': 0,
                     'tvr_08': 1,
                     'tvr_09': 0,
                     'tvr_10': 10,
                     'tvr_11': 0,
                     }
        self.transformed_vector = [[0, 10, 0],
                                   [0.5, 10 + np.sqrt(3) / 2, 0],
                                   [1, 10 + np.sqrt(3), 0],
                                   [-np.sqrt(3)/2, 10.5, 0],
                                   [-np.sqrt(3), 11, 0]]

    def test_init_affine_empty(self):
        assert np.allclose(AffineTransform().affine,
                           np.eye(4))

    def test_init_affine_matrix_from_array(self):
        assert np.allclose(AffineTransform(self.array).affine,
                           self.array)

    def test_init_affine_from_dict(self):
        assert np.allclose(AffineTransform.from_dict(self.dict).affine,
                           self.array)

    def test_affine_to_dict(self):
        affine_dict = AffineTransform(self.array).to_dict()
        for key, value in self.dict.items():
            self.assertAlmostEqual(value, affine_dict[key])

    def test_affine_from_list(self):
        assert np.allclose(AffineTransform.from_list(self.list).affine,
                           self.array)

    def test_affine_to_list(self):
        affine_list = AffineTransform(self.array).to_list()
        assert np.allclose(affine_list, self.list)

    def test_transform_point(self):
        affine_transform = AffineTransform(self.array)
        assert np.allclose(affine_transform.transform(self.point),
                           np.asarray([-np.sqrt(3)/2, 10.5, 0]))

    def test_transform_vector(self):
        affine_transform = AffineTransform(self.array)
        assert np.allclose(affine_transform.transform(self.vector),
                           np.asarray(self.transformed_vector))

    def test_transform_morphology(self):
        transformed_nodes = (AffineTransform(self.array)
                             .transform_morphology(self.morphology)
                             .nodes())

        for node in transformed_nodes:
            assert np.allclose([node['x'], node['y'], node['z']],
                               self.transformed_vector[node['id']])


class TestAffineConstructors(unittest.TestCase):

    def setUp(self):
        self.point = [1, 0, 0]
        self.translation = [10, 0, 0]
        self.rad = 60 * np.pi / 180
        self.c = np.cos(self.rad)
        self.s = np.sin(self.rad)
        self.transform = [[self.c, -self.s, 0], [self.s, self.c, 0], [0, 0, 1]]

    def affine_from_transform_translation_1st(self):
        affine = affine_from_transform_translation(transform=self.transform,
                                                   translation=self.translation,
                                                   translate_first=True)
        assert np.allclose(AffineTransform(affine).transform(self.point),
                           [11 / 2, 11 * np.sqrt(3) / 2, 0])

    def affine_from_transform_translation_2nd(self):
        affine = affine_from_transform_translation(transform=self.transform,
                                                   translation=self.translation)
        assert np.allclose(AffineTransform(affine).transform(self.point),
                           [1 / 2 + 10, np.sqrt(3) / 2, 0])

    def test_rotation_from_angle(self):
        assert np.allclose(rotation_from_angle(self.rad),
                           self.transform)

    def test_affine_from_translation(self):
        assert np.allclose(affine_from_translation(self.translation),
                           [[1, 0, 0, 10],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])

    def test_affine_from_transform(self):
        assert np.allclose(affine_from_transform(self.transform),
                           [[self.c, -self.s, 0, 0],
                            [self.s, self.c, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])
