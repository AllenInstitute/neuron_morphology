from allensdk.neuron_morphology.constants import *


class Colors(object):

    """

    Parameters
    ----------

    soma_color: tuple
        Color of the soma

    axon_color: tuple
        Color of axon

    basal_dendrite_color: tuple
        Color of the basal dendrite

    apical_dendrite_color: tuple
        Color of the apical dendrite

    layer_boundaries_color: tuple
        Color of the layer boundaries

    img_background_color: tuple
        Color of the image background

    scale_bar_color: tuple
        Color of the scale bar

    """

    DEFAULT_SOMA_COLOR = (0, 0, 0)
    DEFAULT_AXON_COLOR = (70, 130, 180)
    DEFAULT_BASAL_DENDRITE_COLOR = (178, 34, 34)
    DEFAULT_APICAL_DENDRITE_COLOR = (255, 127, 80)
    DEFAULT_LAYER_BOUNDARIES_COLOR = (128, 128, 128, 255)
    DEFAULT_IMG_BACKGROUND_COLOR = (255, 255, 255)
    DEFAULT_SCALE_BAR_COLOR = (128, 128, 128, 128)

    def __init__(self, soma_color=DEFAULT_SOMA_COLOR, axon_color=DEFAULT_AXON_COLOR,
                 basal_dendrite_color=DEFAULT_BASAL_DENDRITE_COLOR,
                 apical_dendrite_color=DEFAULT_APICAL_DENDRITE_COLOR,
                 layer_boundaries_color=DEFAULT_LAYER_BOUNDARIES_COLOR,
                 img_background_color=DEFAULT_IMG_BACKGROUND_COLOR,
                 scale_bar_color=DEFAULT_SCALE_BAR_COLOR):

        self._color_by_node_type = {SOMA: soma_color, AXON: axon_color, BASAL_DENDRITE: basal_dendrite_color,
                                    APICAL_DENDRITE: apical_dendrite_color}
        self._layer_boundaries_color = layer_boundaries_color
        self._img_background_color = img_background_color
        self._scale_bar_color = scale_bar_color

    @property
    def soma_color(self):
        return self._color_by_node_type[SOMA]

    @property
    def axon_color(self):
        return self._color_by_node_type[AXON]

    @property
    def basal_dendrite_color(self):
        return self._color_by_node_type[BASAL_DENDRITE]

    @property
    def apical_dendrite_color(self):
        return self._color_by_node_type[APICAL_DENDRITE]

    @property
    def layer_boundaries_color(self):
        return self._layer_boundaries_color

    @property
    def img_background_color(self):
        return self._img_background_color

    @property
    def scale_bar_color(self):
        return self._scale_bar_color

    def get_color_by_node_type(self, node_type):
        return self._color_by_node_type[node_type]
