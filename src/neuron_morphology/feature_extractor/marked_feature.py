
from typing import Set, Callable, Any, Union, Optional, Type, Dict, Sequence, List, TypeVar
from functools import partial
import copy as cp
import inspect

from neuron_morphology.feature_extractor.mark import Mark
from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.feature_extractor.feature_specialization import (
    FeatureSpecialization, SpecializationSet, SpecializationSets, 
    SpecializationOption
)

FeatureFn = Callable[[Data], Any]
M = TypeVar("M", bound="MarkedFeature")

class MarkedFeature:

    __slots__ = ["marks", "feature", "name"]

    def __repr__(self):
        return (
            f"Signature:\n{self.name}{inspect.signature(self.feature)}\n\n"
            f"Marks: {[mark.__name__ for mark in self.marks]}\n\n"
            f"Help:\n{self.feature.__doc__}"
        )

    @property
    def __name__(self):
        return self.name

    def __hash__(self):
        return hash(self.name)

    def __init__(
        self, 
        marks: Set[Type[Mark]], 
        feature: 'Feature', 
        name: Optional[str] = None,
        preserve_marks: bool = True,
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

        self.marks: Set[Type[Mark]] = marks
        self.feature: Feature = feature

        if preserve_marks and hasattr(feature, "marks"):
            self.marks |= set(feature.marks) # type: ignore[union-attr]

        if isinstance(self.feature, MarkedFeature):
            # prevent marked feature chains
            self.feature = self.feature.feature

        if name is not None:
            self.name = name
        elif hasattr(feature, "name"):
            self.name = feature.name # type: ignore[union-attr]
        else:
            self.name = feature.__name__ # type: ignore[union-attr]


    def add_mark(self, mark: Type[Mark]):
        """ Assign an additional mark to this feature
        """

        self.marks.add(mark)

    def __call__(self, *args, **kwargs):
        """ Execute the underlying feature, passing along all arguments
        """

        return self.feature(*args, **kwargs)

    def deepcopy(self, **kwargs):
        """ Make a deep copy of this marked feature
        """

        return MarkedFeature(
            marks=cp.deepcopy(self.marks),
            feature=cp.deepcopy(self.feature),
            name=self.name,
        )

    def partial(self, *args, **kwargs):
        """ Fix one or more parameters on this feature's callable  
        """
        new = self.deepcopy()
        new.feature = partial(new.feature, *args, **kwargs)
        return new

    def specialize(
        self, 
        option: SpecializationOption
    ):
        """ Apply a specialization option to this feature. This binds 
        parameters on the feature's __call__ method, sets 0 or more additional 
        marks, and namespaces the feature's name.

        Parameters
        ----------
        option : The specialization option with which to specialize this 
            feature.

        Returns
        -------
        a deep copy of this feature with updated callable, marks and name

        """

        new = self.partial(**option.kwargs) # type: ignore[misc]
        new.marks |= option.marks
        new.name = f"{option.name}.{new.name}"
        return new

    @classmethod
    def ensure(cls: Type[M], feature: "Feature") -> M:
        """ If a function is not a MarkedFeature, convert it.

        Parameters
        ----------
        feature : the feature to be converted

        Returns
        -------
        Either a marked feature generated from the input, or the input 
            marked feature.

        """
        if not isinstance(feature, cls):
            feature = cls(marks=set(), feature=feature)
        return feature


# The types which are acceptable for use as a feature
Feature = Union[FeatureFn, MarkedFeature]


def specialize(
    feature: Feature, 
    specialization_set:  SpecializationSet
) -> Dict[str, MarkedFeature]:
    """ Bind some of a feature's keyword arguments, using provided 
    specialization options.

    Parameters
    ----------
    feature : will be used as a basis for specialization
    specialization_set : each element defines a particular specialization (i.e 
        a set of keyword argument values and marks) to be applied to the
        feature

    Returns
    -------
    A dictionary mapping (namespaced) feature names to specialized features.
    Note that names are formatted as "specialization_name.base_feature_name"

    """
    
    feature = MarkedFeature.ensure(feature)
    specialized = {}

    for option in specialization_set:
        current = feature.specialize(option)
        specialized[current.name] = current

    return specialized


def nested_specialize(
    feature: Feature,
    specialization_sets: SpecializationSets
) -> Dict[str, MarkedFeature]:
    """ Apply specializations hierarchically to a base feature. Generating a
    new collection of specialized features.

    Parameters
    ----------
    feature : will be used as a basis for specialization
    specialization_sets : each element describes a set of specialization 
        options. The output will have one specialization for each element of the 
        cartesian product of these sets.

    Returns
    -------
    A dictionary mapping namespaced feature names to specialized features.

    Notes
    -----
    Specializations are applied from the start of the specialization_sets to 
    the end. This means that the generated names are structures like:
        "last_spec.middle_spec.first_spec.base_feature_name"

    """

    feature = MarkedFeature.ensure(feature)
    specialized = {feature.name: feature.deepcopy()}

    for spec_set in specialization_sets:
        new_specialized: Dict[str, MarkedFeature] = {}

        for feature in specialized.values():
            new_specialized.update(specialize(feature, spec_set))

        specialized = new_specialized

    return specialized


def marked(mark: Type[Mark]):
    """ Decorator for adding a mark to a function.

    Parameters
    ----------
    mark : the mark to be applied

    Examples
    --------
    @marked(RequiresA)
    @marked(RequiresB)
    def some_feature_requiring_a_and_b(...):
        ...

    """

    def _add_mark(feature):
        return MarkedFeature({mark}, feature)
    return _add_mark
