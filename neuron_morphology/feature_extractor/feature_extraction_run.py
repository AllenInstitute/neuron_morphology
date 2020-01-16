from typing import (
    AbstractSet, Set, Collection, Optional, Dict, Type, FrozenSet, List)
import logging
import warnings

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
        self.selected_features: List[MarkedFeature] = []
        self.provided: Set[FrozenSet[str]] = set([frozenset()])
        self.unsatisfied: Set[MarkedFeature] = set()
        self.results: Optional[Dict] = None

    def select_marks(
        self, 
        marks: Collection[Type[Mark]], 
        required_marks: AbstractSet[Type[Mark]] = frozenset()
    ):
        """ Choose marks for this run by validating a set of candidates 
        against the data.

        Parameters
        ----------
        marks : candidate marks to be validated
        required_marks : if provided, raise an exception if any of these marks
            do not validate successfully

        Returns
        -------
        self : This FeatureExtractionRun, with selected_marks updated

        """

        for mark in marks:
            if mark.validate(self.data):
                self.selected_marks.add(mark)
            else:
                logging.info(f"skipping mark (validation failed): {mark.__class__.__name__}")

        missing_required = required_marks - self.selected_marks
        if missing_required:
            raise ValueError(f"required marks: {missing_required} failed validation!")

        logging.info(f"selected marks: {self.select_marks}")
        return self

    def select_features(
        self, 
        features: Collection[MarkedFeature],
        only_marks: Optional[AbstractSet[Type[Mark]]] = None, 

    ):
        """ Choose features to calculated for this run on the basis of selected
        marks.

        Parameters
        ----------
        features : Candidates features for selection
        only_marks : if provided, reject features not marked with marks in 
            this set

        Returns
        -------
        self : This FeatureExtractionRun, with selected_features updated

        """
        if only_marks is None:
            only_marks = set()

        for feature in features:
            extra_marks = feature.marks - self.selected_marks
            if extra_marks:
                logging.info(
                    f"skipping feature: {feature.name}. "
                    f"Found extra marks: {[mark.__name__ for mark in extra_marks]}")
            elif only_marks - feature.marks:
                logging.info(f"skipping feature: {feature.name} (no marks from {only_marks})")
            else:
                self.select_feature(feature)

        self.resolve_feature_dependencies()
        
        logging.info(f"selected features: {[feature.name for feature in self.selected_features]}")
        return self

    def resolve_feature_dependencies(self):
        """ Iteratively check inter-feature dependencies and select features 
        whose dependencies are satisfied. If a feature's dependencies cannot be 
        satisfied, warn and record the feature.
        """

        old_num_selected = len(self.selected_features)
        new_num_selected = len(self.selected_features) - 1

        while old_num_selected != new_num_selected:

            old_num_selected = len(self.selected_features)

            unsatisfied = self.unsatisfied
            self.unsatisfied = set()

            for to_resolve in unsatisfied:
                self.select_feature(to_resolve)
            
            new_num_selected = len(self.selected_features)

        if len(self.unsatisfied) > 0:
            warnings.warn(
                "unable to satisfy the requirements of the following features:\n\n" + 
                "\n".join([
                    f"feature {feature.name} requires {feature.requires}" 
                    for feature in self.unsatisfied
                ])
            )

    def select_feature(self, feature: MarkedFeature):
        """ Add a feature to this run's selected_features. If its inter-feature 
        dependencies have not been satisfied, instead add it to the set of 
        unsatisfied features

        Parameters
        ----------
        feature : to be added

        """

        if feature.requires in self.provided:
            self.selected_features.append(feature)
            self.provided.add(feature.provides)
        else:
            self.unsatisfied.add(feature)

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

    def serialize(self):
        """ Return a dictionary describing this run
        """

        return {
            "results": self.results,
            "selected_marks": [mark.__name__ for mark in self.selected_marks],
            "selected_features": [
                feature.name for feature in self.selected_features],
            "unsatisfied_features": [
                feature.name for feature in self.unsatisfied]
        }
