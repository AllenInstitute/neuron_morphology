from typing import Set, Callable, Any, Union

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.morphology import Morphology


FeatureFn = Callable[[Morphology], Any]


class MarkedFeature:

    __slots__ = ["marks", "feature", "name"]

    def __init__(self, marks: Set[Mark], feature: Feature):
        """ A feature-calculator with 0 or more marks.

        Parameters
        ----------
        marks : Apply each of these marks to this feature
        feature : The feature to be marked

        """

        self.marks: Set[Mark] = marks
        self.feature: Feature = feature
        
        if hasattr(feature, "name"):
            self.name: str = feature.name
        else:
            self.name: str = feature.__name__

    def add_mark(self, mark: Mark):
        """ Assign an additional mark to this feature
        """

        self.marks.add(mark)

    def __call__(self, *args, **kwargs):
        """ Execute the underlying feature, passing along all arguments
        """
    
        return self.feature(*args, **kwargs)


Feature = Union[FeatureFn, MarkedFeature]


def marked(mark: Mark):
    """ Decorator for adding a mark to a function.

    Parameters
    ----------
    mark : the mark to be applied

    Usage
    -----
    @marked(RequiresA)
    @marked(RequiresB)
    def some_feature_requiring_a_and_b(...):
        ...

    """

    def _add_mark(feature):

        if hasattr(feature, "marks"):
            feature.marks.add(mark)
        else:
            feature = MarkedFeature(set([mark]), feature)

        return feature

    return _add_mark