from typing import Union

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


MorphologyLike = Union[Data, Morphology]

def get_morphology(data: MorphologyLike):
    if isinstance(data, Morphology):
        return data
    return data.morphology
