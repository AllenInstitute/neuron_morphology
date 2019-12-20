from typing import Sequence, Set, AbstractSet, List, Optional
import logging

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.marked_feature import (
    MarkedFeature, Feature
)
from neuron_morphology.feature_extractor.feature_extraction_run import \
    FeatureExtractionRun
from neuron_morphology.feature_extractor.data import Data


class FeatureExtractor:

    def __init__(self, features: Sequence[Feature] = tuple()):
        """ Extracts morphological features from data

        Parameters
        ----------
        features : a sequence of marked (ideally) callables, each of which 
            defines some feature calculation. These define the set of features 
            eligible to be calculated on any specific run

        """

        self.marks: Set[Mark] = set()
        self.features: List[MarkedFeature] = [
            self.register_feature(feature) for feature in features
        ]


    def register_feature(self, feature: Feature):
        """ Add a new feature to the list of options

        Parameters
        ----------
        feature : the feature to be registered. If it is not already marked, 
            it will be registered with no marks

        """

        if not hasattr(feature, "marks"):
            logging.info("please mark your feature")
            feature = MarkedFeature(set(), feature)

        self.marks |= feature.marks
        self.features.append(feature)
        

    def extract(
        self, 
        data: Data, 
        only_marks: Optional[AbstractSet[Mark]] = None, 
        required_marks: AbstractSet[Mark] = frozenset()
    ) -> FeatureExtractionRun:
        """ Run the feature extractor for a single dataset

        Parameters
        ----------
        data : the dataset from which features will be calculated
        only_marks : if provided, reject marks not in this set
        required_marks : if provided, raise an exception if any of these marks
            do not validate successfully

        Returns
        -------
        The calculated features, along with a record of the marks and features
            selected.

        """

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
