from neuron_morphology.morphology import Morphology

class Data:
    """ A placeholder
    """
    
    def __init__(self, morphology: Morphology, **other_things):
        self.morphology: Morphology = morphology
        for name, value in other_things.items():
            setattr(self, name, value)