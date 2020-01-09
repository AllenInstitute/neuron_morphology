from typing import TypeVar, Type, Dict
import inspect

import warnings

from neuron_morphology.feature_extractor.data import Data
from neuron_morphology.constants import (
    SOMA, AXON, BASAL_DENDRITE, APICAL_DENDRITE)


Mr = TypeVar("Mr", bound="Mark")

class Mark:
    """ A tag, intended for use in feature selection.
    """
    @classmethod
    def validate(cls, data: Data) -> bool:
        """ Determine if this feature is calculable from the provided data.

        Parameters
        ----------
        data : Data from a single morphological reconstruction

        Returns
        -------
        whether marked features can be calculated from these data

        """

        return True

    @classmethod
    def factory(cls: Type[Mr], name: str) -> Type[Mr]:
        return type(name, (cls,), {})


class RequiresLayerAnnotations(Mark):
    @classmethod
    def validate(cls, data: Data) -> bool:
        """ Checks whether each node in the data's morphology is annotated with
        a cortical layer. Returns False if any are missing.
        """
        return check_nodes_have_key(data, "layer")


class Intrinsic(Mark):
    """Indicates intrinsic features that don't rely on a ccf or scale."""
    pass


class Geometric(Mark):
    """Indicates features that change depending on coordinate frame."""
    pass


class AllNeuriteTypes(Mark):
    """Indicates features that are calculated for all neurite types."""
    pass


class RequiresDendrite(Mark):
    """This feature can only be calculated for neurons with at least one 
    dendrite node"""

    @classmethod
    def validate(cls, data: Data) -> bool:
        return data.morphology.has_type(APICAL_DENDRITE) \
            or data.morphology.has_type(BASAL_DENDRITE)

class RequiresRelativeSomaDepth(Mark):
    """This feature can only be calculated for relative soma depth"""

    @classmethod
    def validate(cls, data: Data) -> bool:
        return data.morphology.has_type(RELATIVE_SOMA_DEPTH)

class RequiresSoma(Mark):
    """Indicates that these features require a soma."""
    @classmethod
    def validate(cls, data: Data) -> bool:
        return data.morphology.has_type(SOMA)


class RequiresApical(Mark):
    """Indicates that these features require an apical dendrite."""
    @classmethod
    def validate(cls, data: Data) -> bool:
        return data.morphology.has_type(APICAL_DENDRITE)


class RequiresBasal(Mark):
    """Indicates that these features require a basal dendrite."""
    @classmethod
    def validate(cls, data: Data) -> bool:
        return data.morphology.has_type(BASAL_DENDRITE)


class RequiresAxon(Mark):
    """Indicates that these features require an axon."""
    @classmethod
    def validate(cls, data: Data) -> bool:
        return data.morphology.has_type(AXON)


# TODO: this describes the present requirements of root-dependent features. I 
# think that in nearly every case we actually want a RequiresUniqueSomaNode 
# mark
class RequiresRoot(Mark):
    """Indicates that this features require a root. Warns if the root 
    is not unique"""

    @classmethod
    def validate(cls, data: Data) -> bool:
        num_roots = len(data.morphology.get_roots())

        if num_roots > 1:
            warnings.warn(
                f"This morphology is not uniquely rooted! Found {num_roots} "
                "root nodes. Features using the root node of this morphology "
                "may not select that node consistently. Some or all of these "
                "root nodes may not be soma nodes."
            )
        elif num_roots < 1:
            return False

        return True


class BifurcationFeatures(Mark):
    """Indicates a feature calculated on bifurcations."""
    pass


class CompartmentFeatures(Mark):
    """Indicates a feature calculated on compartments."""
    pass


class TipFeatures(Mark):
    """Indicates a feature calculated on tips (leaf nodes)."""
    pass


class NeuriteTypeComparison(Mark):
    """Indicates a feature that is a comparison between neurite types.

    Function should be decorated with the appropriate RequiresType marks
    """
    pass



class RequiresRadii(Mark):
    """ This feature can only be calculated if the radii of nodes are annotated.
    """

    @classmethod
    def validate(cls, data: Data) -> bool:
        return check_nodes_have_key(data, "radius")


class RequiresReferenceLayerDepths(Mark):
    """ This feature can only be calculated if a referenceset of average depths 
    for cortical layers is provided. See features.layer.reference_layer_depths
    for more information.
    """

    @classmethod
    def validate(cls, data: Data) -> bool:
        return hasattr(data, "reference_layer_depths")


class RequiresLayeredPointDepths(Mark):
    """ This feature can only be calculated if (cortical) points are annotated 
    with a collection of within-layer depths. See 
    features.layer.layered_point_depths for more information.
    """

    @classmethod
    def validate(cls, data: Data) -> bool:
        return hasattr(data, "layered_point_depths")



class RequiresRegularPointSpacing(Mark):
    """ This features can only be (meaningfully) calculated if the points (e.g.
    node positions) on which it is based are resampled to have regular spacing.
    """



def check_nodes_have_key(data: Data, key: str) -> bool:
    """ Checks whether each node in a morphology is annotated with some key.
    """

    has_key = True
    for node in data.morphology.nodes():
        has_key = has_key and key in node
        if not has_key:
            break

    return has_key
