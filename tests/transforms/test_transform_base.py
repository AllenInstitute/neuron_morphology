import unittest

from neuron_morphology.transforms.transform_base import TransformBase


class TestTransformBase(unittest.TestCase):

    def test_cannot_instantiate(self):
        with self.assertRaises(TypeError):
            TransformBase()

    def test_missing_transform_method(self):

        class ConcreteTransform(TransformBase):
            def transform_morphology(self):
                return "implements transform_morphology but not transform"

        with self.assertRaises(TypeError):
            ConcreteTransform()

    def test_missing_transform_morphology_method(self):

        class ConcreteTransform(TransformBase):
            def transform(self):
                return "implements transform but not transform_morphology"

        with self.assertRaises(TypeError):
            ConcreteTransform()

    def test_concrete(self):

        class ConcreteTransform(TransformBase):
            def transform_morphology(self):
                return "implements transform_morphology"

            def transform(self):
                return "implements transform"

        ConcreteTransform()
        assert True
