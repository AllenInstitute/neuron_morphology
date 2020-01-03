from typing import NamedTuple, Set, Dict, Any, Sequence, Type
import abc

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
from neuron_morphology.feature_extractor.marked_feature import (
    MarkedFeature, Feature
)


class FeatureSpecialization(metaclass=abc.ABCMeta):

    @property
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def marks(self) -> Set[Mark]:
        pass

    @property
    @abc.abstractmethod
    def kwargs(self) -> Dict[str, Any]:
        pass


def specialize_feature(
    feature: Feature, 
    specializations: Set[Type[FeatureSpecialization]]
) -> Dict[str, MarkedFeature]:

    if not isinstance(feature, MarkedFeature):
        feature = MarkedFeature(set(), feature)

    specialized = {}

    for spec in specializations:
        full_name = f"{spec.name}.{feature.name}"
        specialized[full_name] = MarkedFeature(
            marks=spec.marks,
            feature=feature.partial(**spec.kwargs),
            name=full_name
        )

    return specialized


def nested_specialize(
    feature: Feature,
    specializations: Sequence[Set[FeatureSpecialization]],
) -> Dict:
    """ 
    """

    specialized = {feature.name: feature}

    for spec_set in specializations:
        new_specialized = {}

        for feature in specialized.values():
            new_specialized.update(specialize_feature(feature, spec_set))

        specialized = new_specialized

    return specialized


class AxonSpec:#(FeatureSpecialization):
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
