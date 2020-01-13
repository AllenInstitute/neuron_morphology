from typing import Union, Any, Dict

from neuron_morphology.morphology import Morphology

class Data:

    def __init__(self, morphology: Morphology, **other_things):
        """ A placeholder for the "general data" objsect that we will pass 
        into the feature extractor. Guaranteed to have a morphology. Might 
        have other things.
        """

        self.morphology: Morphology = morphology
        for name, value in other_things.items():
            setattr(self, name, value)

    def __hash__(self):
        return hash(id(self))

# Using get_morphology, functions can easily accept either a Data or a 
# Morphology. This derived type expresses that union.
MorphologyLike = Union[Data, Morphology]

def get_morphology(data: MorphologyLike):
    """ Decay a Data to a Morphology, leaving Morphologies untouched
    """

    if isinstance(data, Morphology):
        return data
    return data.morphology
