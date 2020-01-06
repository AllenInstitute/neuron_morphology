import math

from neuron_morphology.constants import SOMA

def calculate_soma_surface(morphology):

    """
        Approximates the surface area of the soma. Morphologies with only
        a single soma node are supported.

        Parameters
        ----------
        morphology: Morphology object

        Returns
        -------

        Scalar value

    """

    soma = morphology.get_root()
    return 4.0 * math.pi * soma['radius'] * soma['radius']


def calculate_relative_soma_depth(morphology):
    """
        Calculate the soma depth relative to pia/wm
        
        Parameters
        ----------
        morphology: Morphology object

        Returns
        -------

        Scalar value

    """




def calculate_soma_features(morphology, soma_depth):

    features = {}
    features["soma_surface"] = calculate_soma_surface(morphology)
    features["relative_soma_depth"] = soma_depth

    return features
