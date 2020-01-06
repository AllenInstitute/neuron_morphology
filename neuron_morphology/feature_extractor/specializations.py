from enum import Enum

from neuron_morphology import constants as c


class NODESET(Enum):
    AXON = [c.AXON]
    APICAL_DENDRITE = [c.APICAL_DENDRITE]
    BASAL_DENDRITE = [c.BASAL_DENDRITE]
    DENDRITE = [c.APICAL_DENDRITE, c.BASAL_DENDRITE]
    ALL = None
