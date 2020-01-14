import unittest

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.marked_feature import marked, require
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

        @require("baz")
        def fish(data):
            return 12
        self.fish = fish

    def test_select_marks(self):
        run = (
            FeatureExtractionRun(Data(self.morphology, a=2, b=4))
                .select_marks([self.amark, self.bmark])
        )

        self.assertEqual(run.selected_marks, {self.amark})

    def test_select_marks_required(self):
        with self.assertRaises(ValueError):
            (
                FeatureExtractionRun(Data(self.morphology, a=2, b=4))
                    .select_marks(
                        [self.amark, self.bmark],
                        required_marks={self.bmark}
                    )
            )

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

    def test_resolve_feature_dependencies(self):
        run = FeatureExtractionRun(Data(self.morphology))
        run.select_feature(self.foo)
        run.select_feature(self.baz)
        run.unsatisfied = {self.fish}
        run.resolve_feature_dependencies()
        self.assertEqual(set(run.selected_features), 
            {self.foo, self.baz, self.fish})

    def test_resolve_feature_dependencies_missing(self):
        run = FeatureExtractionRun(Data(self.morphology))
        run.select_feature(self.foo)
        run.unsatisfied = {self.fish}
        with self.assertWarns(UserWarning):
            run.resolve_feature_dependencies()
        self.assertEqual(set(run.selected_features), 
            {self.foo})

    def test_select_feature_satisfied(self):
        run = FeatureExtractionRun(Data(self.morphology))
        run.provided = {frozenset(["baz"])}
        run.select_feature(self.fish)
        self.assertEqual(set(run.selected_features), {self.fish})
        self.assertEqual(
            run.provided, {frozenset(["baz"]), frozenset(["fish"])})

    def test_select_feature_unsatisfied(self):
        run = FeatureExtractionRun(Data(self.morphology))
        run.provided = set()
        run.select_feature(self.fish)
        self.assertEqual(set(run.selected_features), set())
        self.assertEqual(run.provided, set())

    def test_extract(self):
        run = FeatureExtractionRun(Data(self.morphology, a=2, b=4))
        run.selected_features = [self.foo]
        run.extract()

        self.assertEqual(run.results["foo"], True)
        self.assertEqual(len(run.results), 1)
