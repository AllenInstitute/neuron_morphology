from neuron_morphology.feature_extractor.data import Data

class Mark:

    def validate(self, data: Data) -> bool:
        return True


class RequiresLayerAnnotations(Mark):

    def validate(self, data: Data) -> bool:

        has_layers = True
        for node in data.morphology.nodes:
            has_layers = has_layers and "layer" in node
            if not has_layers:
                break

        return has_layers
