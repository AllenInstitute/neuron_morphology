from typing import (
    NamedTuple, Set, Dict, Any, Sequence, Type, List, TypeVar, Optional)
import abc
import copy as cp

from neuron_morphology.constants import (
    AXON,
    APICAL_DENDRITE,
    BASAL_DENDRITE,
    SOMA
)

from neuron_morphology.feature_extractor.mark import (
    Mark, 
    RequiresAxon,
    RequiresApical,
    RequiresBasal,
    RequiresDendrite,
    AllNeuriteTypes
)


Fs = TypeVar("Fs", bound="FeatureSpecialization")


class FeatureSpecialization(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def marks(self) -> Set[Type[Mark]]:
        pass

    @property
    @abc.abstractmethod
    def kwargs(self) -> Dict[str, Any]:
        pass

    @classmethod
    def factory(
        cls: Type[Fs], 
        name: str, 
        marks: Set[Type[Mark]], 
        kwargs: Dict[str, Any], 
        display_name: Optional[str] = None
    ) -> Type[Fs]:
        """ A utility for quickly generating feature specializations

        Parameters
        ----------
        name : The name of the generated class. If display_name is not 
            provided, this will also be used as the name attribute of the 
            generated class
        marks : the marks which this specialization implies.
        kwargs : the keyword argument values defining this specialization
        display_name : if provided, the name attribute of the generated 
            specialization.

        Returns
        -------
        A generated FeatureSpecialization subclass

        """

        if display_name is None:
            display_name = name

        return type(
            name,
            (cls,),
            {
                "name": display_name,
                "marks": cp.deepcopy(marks),
                "kwargs": cp.deepcopy(kwargs)
            }
        )


SpecializationOption = Type[FeatureSpecialization]
SpecializationSet = Set[SpecializationOption]
SpecializationSets = List[SpecializationSet]


class AxonSpec(FeatureSpecialization):
    name="axon"
    marks={RequiresAxon}
    kwargs={"node_types": [AXON]}

class ApicalDendriteSpec(FeatureSpecialization):
    name="apical_dendrite"
    marks={RequiresApical}
    kwargs={"node_types": [APICAL_DENDRITE]}

class BasalDendriteSpec(FeatureSpecialization):
    name="basal_dendrite"
    marks={RequiresBasal}
    kwargs={"node_types": [BASAL_DENDRITE]}

class DendriteSpec(FeatureSpecialization):
    name="dendrite"
    marks={RequiresDendrite}
    kwargs={"node_types": [APICAL_DENDRITE, BASAL_DENDRITE]}

class AllNeuriteSpec(FeatureSpecialization):
    name="all_neurites"
    marks={AllNeuriteTypes}
    kwargs={"node_types": None}


NEURITE_SPECIALIZATIONS = {
    AxonSpec,
    ApicalDendriteSpec,
    BasalDendriteSpec,
    DendriteSpec,
    AllNeuriteSpec
}

class AxonCompareSpec(FeatureSpecialization):
    name="axon"
    marks={RequiresAxon}
    kwargs={"node_types_to_compare": [AXON]}

class ApicalDendriteCompareSpec(FeatureSpecialization):
    name="apical_dendrite"
    marks={RequiresApical}
    kwargs={"node_types_to_compare": [APICAL_DENDRITE]}

class BasalDendriteCompareSpec(FeatureSpecialization):
    name="basal_dendrite"
    marks={RequiresBasal}
    kwargs={"node_types_to_compare": [BASAL_DENDRITE]}

class DendriteCompareSpec(FeatureSpecialization):
    name="dendrite"
    marks={RequiresDendrite}
    kwargs={"node_types_to_compare": [APICAL_DENDRITE, BASAL_DENDRITE]}

class AllNeuriteCompareSpec(FeatureSpecialization):
    name="all_neurites"
    marks={AllNeuriteTypes}
    kwargs={"node_types_to_compare": None}


NEURITE_COMPARISON_SPECIALIZATIONS = {
    AxonCompareSpec,
    ApicalDendriteCompareSpec,
    BasalDendriteCompareSpec,
    DendriteCompareSpec,
    AllNeuriteCompareSpec
}