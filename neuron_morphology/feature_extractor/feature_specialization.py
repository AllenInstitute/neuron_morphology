from typing import NamedTuple, Set, Dict, Any, Sequence, Type, List
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
    def factory(cls, name, marks, kwargs, display_name=None):
        if display_name is None:
            display_name = name

        return type(
            name,
            (cls,),
            {
                "name": name,
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


COMPREHENSIVE_NEURITE_SPECIALIZATIONS = {
    AxonSpec,
    ApicalDendriteSpec,
    BasalDendriteSpec,
    DendriteSpec,
    AllNeuriteSpec
}
