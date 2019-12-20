from typing import Sequence, Callable, Set, AbstractSet, List, Optional
import logging

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.marked_feature import (
    MarkedFeature, Feature
)
from neuron_morphology.feature_extractor.feature_extraction_run import \
    FeatureExtractionRun
from neuron_morphology.feature_extractor.data import Data


class FeatureExtractor:

    def __init__(self, features: Sequence[Callable] = tuple()):
        self.marks: Set[Mark] = set()
        self.features: List[MarkedFeature] = [
            self.register_feature(feature) for feature in features
        ]


    def register_feature(self, feature: Feature):
        if not hasattr(feature, "marks"):
            logging.info("please mark your feature")
            feature = MarkedFeature(set(), feature)

        self.marks |= feature.marks
        self.features.append(feature)
        

    def pipeline(
        self, 
        data: Data, 
        only_marks: Optional[AbstractSet[Mark]] = None, 
        required_marks: AbstractSet[Mark] = frozenset()
    ):
        return (
            FeatureExtractionRun(data)
                .select_marks(
                    self.marks, 
                    only_marks=only_marks, 
                    required_marks=required_marks
                )
                .select_features(self.features)
                .extract()
        )
