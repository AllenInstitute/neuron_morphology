from typing import Set, Callable, Any, Union, Optional
from functools import partial

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.data import Data


FeatureFn = Callable[[Data], Any]


class MarkedFeature:

    __slots__ = ["marks", "feature", "name"]

    def __init__(
        self, 
        marks: Set[Mark], 
        feature: 'Feature', 
        name: Optional[str] = None,
        preserve_marks: bool = True
    ):
        """ A feature-calculator with 0 or more marks.

        Parameters
        ----------
        marks : Apply each of these marks to this feature
        feature : The feature to be marked
        name : The display name of this feature. If not provided it will be 
            inferred
        preserve_marks : If True, any marks on the underlying feature will 
            be retained. Otherwise they will be discarded.

        """

        self.marks: Set[Mark] = marks
        self.feature: Feature = feature

        if preserve_marks and hasattr(feature, "marks"):
            self.marks |= set(feature.marks)

        if isinstance(self.feature, MarkedFeature):
            # prevent marked feature chains
            self.feature = self.feature.feature

        if name is not None:
            self.name = name
        elif hasattr(feature, "name"):
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

    def partial(self, *args, **kwargs):
        return MarkedFeature(
            marks=self.marks,
            feature=partial(self.feature, *args, **kwargs),
            name=self.name
        )


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
        return MarkedFeature({mark}, feature)

    return _add_mark