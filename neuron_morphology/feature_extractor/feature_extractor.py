from typing import Sequence, Callable, Set, Optional
import logging
import copy

from neuron_morphology.morphology import Morphology
from neuron_morphology.feature_extractor.mark import Mark, MarkedFn


class FeatureExtractor:

    def __init__(self, features: Sequence[Callable] = tuple()):
        self.marks: Set[Mark] = set()
        self.features: Sequence[Callable] = [
            self.register_feature(feature) for feature in features
        ]


    def register_feature(self, feature: Callable):
        if not hasattr(feature, "marks"):
            logging.info("please mark your feature")
            feature = MarkedFn(set(), feature)

        self.marks |= feature.marks
        self.features.append(feature)
        

    def pipeline(self, morphology, only_marks=None, required_marks=set()):
        return (
            FeatureExtractionRun(morphology)
                .select_marks(
                    self.marks, 
                    only_marks=only_marks, 
                    required_marks=required_marks
                )
                .select_features(self.features)
                .extract()
        )


class FeatureExtractionRun:
    
    def __init__(self, morphology):
        self.morphology = morphology

        self.selected_marks = set()
        self.selected_features = set()
        self.results = None

    def select_marks(self, marks, only_marks: Optional[Set[Mark]] = None, required_marks: Set[Mark] = set()):

        for mark in marks:
            if mark.validate(self.morphology):
                if only_marks is None or mark in only_marks:
                    self.selected_marks.add(mark)
                else:
                    logging.info(f"skipping mark (excluded by only): {mark.__class__.__name__}")
            else:
                logging.info(f"skipping mark (validation failed): {mark.__class__.__name__}")

        missing_required = required_marks - self.selected_marks
        if missing_required:
            raise ValueError(f"required marks: {missing_required} failed validation!")

        logging.info(f"selected marks: {self.select_marks}")
        return self

    def select_features(self, features):

        for feature in features:
            if feature.marks - self.selected_marks:
                logging.info(f"skipping feature: {feature.name}")
            else:
                self.selected_features.add(feature)
        
        logging.info(f"selected features: {[feature.name for feature in self.selected_features]}")
        return self

    def extract(self):
        self.results = {}

        for feature in self.selected_features:
            try:
                self.results[feature.name] = feature(self.morphology)
            except:
                logging.warning(f"feature extraction failed for {feature.name}")
                raise

        return self