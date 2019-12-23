from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.constants import (
    SOMA, AXON, BASAL_DENDRITE, APICAL_DENDRITE)


class Mark:
    """ A tag, intended for use in feature selection.
    """

    def validate(self, data: Data) -> bool:
        """ Determine if this feature is calculable from the provided data.

        Parameters
        ----------
        data : Data from a single morphological reconstruction

        Returns
        -------
        whether marked features can be calculated from these data

        """

        return True


class RequiresLayerAnnotations(Mark):

    def validate(self, data: Data) -> bool:
        """ Checks whether each node in the data's morphology is annotated with
        a cortical layer. Returns False if any are missing.
        """

        has_layers = True
        for node in data.morphology.nodes:
            has_layers = has_layers and "layer" in node
            if not has_layers:
                break

        return has_layers


class Intrinsic(Mark):
    """Indicates intrinsic features that don't rely on a ccf or scale."""
    pass


class Geometric(Mark):
    """Indicates features that change depending on coordinate frame."""
    pass


class AllNeuriteTypes(Mark):
    """Indicates features that are calculated for all neurite types."""
    pass


class RequiresSoma(Mark):
    """Indicates that these features require a soma."""
    def validate(self, data: Data) -> bool:
        return data.morphology.has_type(SOMA)


class RequiresApical(Mark):
    """Indicates that these features require an apical dendrite."""
    def validate(self, data: Data) -> bool:
        return data.morphology.has_type(APICAL_DENDRITE)


class RequiresBasal(Mark):
    """Indicates that these features require a basal dendrite."""
    def validate(self, data: Data) -> bool:
        return data.morphology.has_type(BASAL_DENDRITE)


class RequiresAxon(Mark):
    """Indicates that these features require an axon."""
    def validate(self, data: Data) -> bool:
        return data.morphology.has_type(AXON)


class BifurcationFeatures(Mark):
    """Indicates a feature calculated on bifurcations."""
    pass


class CompartmentFeatures(Mark):
    """Indicates a feature calculated on compartments."""
    pass


class NeuriteTypeComparison(Mark):
    """Indicates a feature that is a comparison between neurite types.

    Function should be decorated with the appropriate RequiresType marks
    """
    pass
