import unittest

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.marked_feature import (
    MarkedFeature, specialize, nested_specialize)
from neuron_morphology.feature_extractor.feature_specialization import \
    FeatureSpecialization


class TestSpecialization(unittest.TestCase):

    def setUp(self):

        def multiply(a, by=2, add=0):
            return a*by + add
        self.multiply = multiply

        self.uses_four = Mark.factory("UsesFour") 
        self.uses_five = Mark.factory("UsesFive") 
        self.uses_six = Mark.factory("UsesSix") 
        self.uses_seven = Mark.factory("UsesSeven")
        self.does_math = Mark.factory("DoesMath")

        self.by4 = FeatureSpecialization.factory("By4", {self.uses_four}, {"by": 4})
        self.by5 = FeatureSpecialization.factory("By5", {self.uses_five}, {"by": 5})
        self.add6 = FeatureSpecialization.factory("Add6", {self.uses_six}, {"add": 6})
        self.add7 = FeatureSpecialization.factory("Add7", {self.uses_seven}, {"add": 7})

    def test_specialize_method(self):
        multiply_by_4 = MarkedFeature.ensure(self.multiply).specialize(self.by4)
        self.assertEqual(multiply_by_4(2), 8)
        self.assertEqual(multiply_by_4.marks, {self.uses_four})

    def test_specialize_fn(self):
        multipliers = specialize(self.multiply, {self.by4})
        multiply_by_4 = multipliers["By4.multiply"]

        self.assertEqual(multiply_by_4(2), 8)
        self.assertEqual(multiply_by_4.marks, {self.uses_four})

    def test_specialize_marked(self):
        multiply = MarkedFeature({self.does_math}, self.multiply)
        multiply_by_4 = specialize(multiply, {self.by4})["By4.multiply"]

        self.assertEqual(multiply_by_4(2), 8)
        self.assertEqual(multiply_by_4.marks, {self.uses_four, self.does_math})

    def test_nested_specialize(self):
        multipliers = nested_specialize(
            self.multiply, [{self.by4, self.by5}, {self.add6, self.add7}]
        )

        self.assertEqual(
            multipliers["Add7.By4.multiply"](2),
            15
        )
        self.assertEqual(
            multipliers["Add6.By5.multiply"].marks,
            {self.uses_five, self.uses_six}
        )
