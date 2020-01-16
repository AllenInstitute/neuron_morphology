import unittest

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.marked_feature import marked
from neuron_morphology.feature_extractor.feature_extraction_run import \
    FeatureExtractionRun
from neuron_morphology.morphology_builder import MorphologyBuilder

class TestFeatureExtractionRun(unittest.TestCase):
    
    def setUp(self):

        # we are not actually going to use this - but it must be argued to the 
        # Data constructor
        self.morphology = (
            MorphologyBuilder()
                .root()
                .build()
        )

        class AMark(Mark):
            @classmethod
            def validate(cls, data):
                return hasattr(data, "a") and data.a == 2
        self.amark = AMark

        class BMark(Mark):
            @classmethod
            def validate(cls, data):
                return hasattr(data, "b") and data.b == 3
        self.bmark = BMark

        @marked(AMark)
        def foo(data):
            return data.a == 2
        self.foo = foo

        @marked(BMark)
        def baz(data):
            return data.b == 3
        self.baz = baz


    def test_select_marks(self):
        run = (
            FeatureExtractionRun(Data(self.morphology, a=2, b=4))
                .select_marks([self.amark, self.bmark])
        )

        self.assertEqual(run.selected_marks, {self.amark})


    def test_select_features(self):
        run = (
            FeatureExtractionRun(Data(self.morphology, a=2, b=4))
                .select_marks([self.amark, self.bmark])
                .select_features([self.foo, self.baz])
        )
        self.assertEqual(set(run.selected_features), {self.foo})

    def test_select_features_only(self):
        run = (
            FeatureExtractionRun(Data(self.morphology, a=2, b=4))
                .select_marks([self.amark, self.bmark])
                .select_features([self.foo, self.baz], only_marks={self.bmark})
        )
        self.assertEqual(set(run.selected_features), set())

    def test_extract(self):
        run = FeatureExtractionRun(Data(self.morphology, a=2, b=4))
        run.selected_features = [self.foo]
        run.extract()

        self.assertEqual(run.results["foo"], True)
        self.assertEqual(len(run.results), 1)
