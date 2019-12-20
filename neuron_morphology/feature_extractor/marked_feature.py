from typing import Set, Callable, Any, Union

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.morphology import Morphology


FeatureFn = Callable[[Morphology], Any]


class MarkedFeature:

    __slots__ = ["marks", "feature", "name"]

    def __init__(self, marks: Set[Mark], feature: Feature):
        self.marks: Set[Mark] = marks
        self.feature: Feature = feature
        
        if hasattr(feature, "name"):
            self.name: str = feature.name
        else:
            self.name: str = feature.__name__

    def add_mark(self, mark: Mark):
        self.marks.add(mark)

    def __call__(self, *args, **kwargs):
        return self.feature(*args, **kwargs)


Feature = Union[FeatureFn, MarkedFeature]


def marked(mark):

    def _add_mark(feature):

        if hasattr(feature, "marks"):
            feature.marks.add(mark)
        else:
            feature = MarkedFeature(set([mark]), feature)

        return feature

    return _add_mark