from typing import Sequence, Set, AbstractSet, List, Optional, Type
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

        self.marks: Set[Type[Mark]] = set()
        self.features: List[MarkedFeature] = []

        if features:
            self.register_features(features)

    def register_features(self, features: Sequence[Feature]):
        """ Add a new feature to the list of options

        Parameters
        ----------
        features : the features to be registered. If it is not already marked,
            it will be registered with no marks

        """
        for feature in features:

            if isinstance(feature, dict):
                specialized_features = feature.values()
            elif isinstance(feature, (list, tuple)):
                specialized_features = feature
            elif not isinstance(feature, MarkedFeature):
                specialized_features = [MarkedFeature.ensure(feature)]
            else:
                specialized_features = [feature]

            for specialized_feature in specialized_features:
                self.marks |= specialized_feature.marks
                self.features.append(specialized_feature)

    def extract(
        self,
        data: Data,
        only_marks: Optional[AbstractSet[Type[Mark]]] = None,
        required_marks: AbstractSet[Type[Mark]] = frozenset()
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
