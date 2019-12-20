from neuron_morphology.feature_extractor.data import Data

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
