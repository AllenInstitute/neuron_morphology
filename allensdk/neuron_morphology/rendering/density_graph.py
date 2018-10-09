import numpy as np
from PIL import ImageDraw, Image
from functools import reduce
import math
import allensdk.neuron_morphology.rendering.colors as co


class DensityGraph(object):

    def __init__(self, morphology, width, height, soma_depth, relative_soma_depth, ordered_node_types,
                 colors=co.Colors()):

        self._soma_depth = soma_depth
        self._width = width
        self._height = height
        self._relative_soma_depth = relative_soma_depth
        self._morphology = morphology
        self._ordered_node_types = ordered_node_types
        self._colors = colors
        self._histograms_by_type = {node_type: CorticalDepthHistogram(self._height, self._soma_depth,
                                                                      self._relative_soma_depth)
                                    for node_type in self._ordered_node_types}

        for compartment in self._morphology.get_compartment_list():
            weight = morphology.get_compartment_length(compartment) / 2
            for node in compartment:
                if node['type'] in self._histograms_by_type:
                    self._histograms_by_type[node['type']].add(node, weight)

    def draw_histograms(self):

        img = Image.new("RGBA", (self._width, self._height))
        canvas = ImageDraw.Draw(img)

        histogram_max = self.max()

        for node_type in self._ordered_node_types:
            self._histograms_by_type[node_type].draw_histogram(canvas, self._width, self._height,
                                                               self._colors.get_color_by_node_type(node_type),
                                                               histogram_max)

        self._draw_layer_boundaries(canvas)

        return img

    def max(self):
        return reduce(max, map(CorticalDepthHistogram.max, self._histograms_by_type.values()))

    def top(self):
        return reduce(min, map(CorticalDepthHistogram.top, self._histograms_by_type.values()))

    def bottom(self):
        return reduce(max, map(CorticalDepthHistogram.bottom, self._histograms_by_type.values()))

    def _draw_layer_boundaries(self, canvas):

        # draw layer boundaries
        number_of_layers = 5

        canvas.line((0, 0, 0, self._height), self._colors.layer_boundaries_color)
        for i in range(number_of_layers):
            canvas.line((0, (i * self._height / number_of_layers), self._width, (i * self._height / number_of_layers)),
                        self._colors.layer_boundaries_color)

        canvas.line((0, self._height - 1, self._width, self._height - 1), self._colors.layer_boundaries_color)


class CorticalDepthHistogram(object):

    def __init__(self, number_of_bins, soma_depth, relative_soma_depth):

        self._number_of_bins = number_of_bins
        self._histogram = np.zeros(self._number_of_bins)
        self._soma_depth = soma_depth
        self._relative_soma_depth = relative_soma_depth

    @property
    def number_of_bins(self):
        return self._number_of_bins

    @property
    def histogram(self):
        return self._histogram

    def add(self, node, weight):
        cortical_depth = abs(self._convert_y_value_to_cortical_depth(node['y']))
        bin_index = self._convert_cortical_depth_to_bin_index(cortical_depth)
        self.histogram[bin_index] += weight

    def _convert_cortical_depth_to_bin_index(self, cortical_depth):
        cortical_depth_length = 1.0
        bin_size = cortical_depth_length / self._number_of_bins
        bin_index = int(math.floor(cortical_depth / bin_size))
        return bin_index

    def _convert_y_value_to_cortical_depth(self, y_value):
        return y_value * (self._relative_soma_depth / self._soma_depth)

    def max(self):
        return self._histogram.max()

    def top(self):
        return np.nonzero(self._histogram)[0][0]

    def bottom(self):
        non_zero_elements = np.nonzero(self._histogram)[0]
        return non_zero_elements[len(non_zero_elements) - 1]

    def draw_histogram(self, canvas, width, height, color, histogram_max):

        histogram_step = height / self._number_of_bins
        histogram_scale = (width - 1) / histogram_max

        y0 = 0
        for i in range(self._number_of_bins):
            y1 = int(y0 + histogram_step)
            x0 = 1
            x1 = x0
            x1 += int(self.histogram[i] * histogram_scale + 0.99)
            if x1 > width:
                x1 = width
            if x0 != x1:
                canvas.line((x0, int(y1), x1, int(y1)), color)
                y1 += histogram_step
            y0 += histogram_step

    def __repr__(self):
        return "Number of Bins: %s\nHistogram: %s" % (self._number_of_bins, self._histogram)
