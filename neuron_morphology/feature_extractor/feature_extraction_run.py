from typing import AbstractSet, Set, Collection, Optional, Dict, Type
import logging

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.marked_feature import MarkedFeature
from neuron_morphology.feature_extractor.mark import Mark


class FeatureExtractionRun:
    
    def __init__(self, data):
        """ Represents a single run of feature extraction on a single dataset.

        Parameters
        ----------
        data : the dataset from which to extract features

        """

        self.data: Data = data

        self.selected_marks: Set[Type[Mark]] = set()
        self.selected_features: Set[MarkedFeature] = set()
        self.results: Optional[Dict] = None

    def select_marks(
        self, 
        marks: Collection[Type[Mark]], 
        only_marks: Optional[AbstractSet[Type[Mark]]] = None, 
        required_marks: AbstractSet[Type[Mark]] = frozenset()
    ):
        """ Choose marks for this run by validating a set of candidates 
        against the data.

        Parameters
        ----------
        marks : candidate marks to be validated
        only_marks : if provided, reject marks not in this set
        required_marks : if provided, raise an exception if any of these marks
            do not validate successfully

        Returns
        -------
        self : This FeatureExtractionRun, with selected_marks updated

        """

        for mark in marks:
            if mark.validate(self.data):
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

    def select_features(self, features: Collection[MarkedFeature]):
        """ Choose features to calculated for this run on the basis of selected
        marks.

        Parameters
        ----------
        features : Candidates features for selection

        Returns
        -------
        self : This FeatureExtractionRun, with selected_features updated

        """

        for feature in features:
            if feature.marks - self.selected_marks:
                logging.info(f"skipping feature: {feature.name}")
            else:
                self.selected_features.add(feature)
        
        logging.info(f"selected features: {[feature.name for feature in self.selected_features]}")
        return self

    def extract(self):
        """ For each selected feature, carry out calculation on this run's 
        dataset.

        Returns
        -------
        self : This FeatureExtractionRun, with results updated
        """

        self.results = {}

        for feature in self.selected_features:
            try:
                self.results[feature.name] = feature(self.data)
            except:
                logging.warning(f"feature extraction failed for {feature.name}")
                raise

        return self