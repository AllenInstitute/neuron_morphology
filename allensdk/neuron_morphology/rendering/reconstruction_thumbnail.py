from allensdk.neuron_morphology.constants import *
from PIL import Image, ImageDraw
import numpy as np


class MorphologySummary(object):

    """ Class to create thumbnails for neuron reconstructions

    :parameter morphology: morphology
            object created from an swc file that is being drawn
    :parameter soma_depth: int
            distance from soma to pia
    :parameter relative_soma_depth: int
            soma depth divided by the distance between pia and white matter
    :parameter soma_color: tuple
            color of the soma
    :parameter axon_color: tuple
            color of axon
    :parameter basal_dendrite_color: tuple
            color of the basal dendrite
    :parameter apical_dendrite_color: tuple
            color of the apical dendrite
    :parameter layer_boundaries_color: tuple
            color of the layer boundaries
    :parameter original_scale: boolean
            flag to indicate whether the original scale should be used

    """

    DEFAULT_SOMA_DEPTH = 0
    DEFAULT_RELATIVE_SOMA_DEPTH = 0
    DEFAULT_SOMA_COLOR = (0, 0, 0)
    DEFAULT_AXON_COLOR = (70, 130, 180)
    DEFAULT_BASAL_DENDRITE_COLOR = (178, 34, 34)
    DEFAULT_APICAL_DENDRITE_COLOR = (255, 127, 80)
    DEFAULT_LAYER_BOUNDARIES_COLOR = (128, 128, 128, 255)
    DEFAULT_ORIGINAL_SCALE = True
    DEFAULT_SCALE_BAR_COLOR = (128, 128, 128, 128)
    DEFAULT_LINE_COLOR = (128, 128, 128, 255)
    DRAW_AXON_FIRST = True

    def __init__(self, morphology, soma_depth=DEFAULT_SOMA_DEPTH, relative_soma_depth=DEFAULT_RELATIVE_SOMA_DEPTH,
                 soma_color=DEFAULT_SOMA_COLOR, axon_color=DEFAULT_AXON_COLOR,
                 basal_dendrite_color=DEFAULT_BASAL_DENDRITE_COLOR, apical_dendrite_color=DEFAULT_APICAL_DENDRITE_COLOR,
                 layer_boundaries_color=DEFAULT_LAYER_BOUNDARIES_COLOR, original_scale=DEFAULT_ORIGINAL_SCALE):

        self.morphology = morphology
        self.soma_depth = soma_depth
        self.relative_soma_depth = relative_soma_depth
        self.soma_color = soma_color
        self.axon_color = axon_color
        self.basal_dendrite_color = basal_dendrite_color
        self.apical_dendrite_color = apical_dendrite_color
        self.layer_boundaries_color = layer_boundaries_color
        self.original_scale = original_scale

    def __transform_swc_to_pia_space(self, pia_transform):

        """ Transforms the morphology to pia space

        :parameter pia_transform:
        :return:
        """

        # construct affine transform
        aff = np.zeros(12)
        for i in range(12):
            aff[i] = pia_transform["tvr_%02d" % i]

        nrn = self.morphology

        # transform to pia-space
        nrn_transform = nrn.clone()
        nrn_transform.apply_affine(aff)

        # draw compartments
        # order them by depth to approximate 3D rendering
        sorted(nrn_transform.compartment_list, key=lambda x: x.node1.y)

        return nrn_transform

    def __set_scale(self, image_height):

        """ Sets the scale for the reconstruction

        :parameter image_height: int
                the height of the thumbnail that is being generated
        :return: scale: int
                A scalar amount that is multiplied to morphology coordinates before drawing
        """

        if self.original_scale:
            scale = self.soma_depth / self.relative_soma_depth
        else:
            scale = image_height / (self.soma_depth / self.relative_soma_depth)

        return scale

    def __set_color_by_node_type(self, segment):

        """ Sets the color of the segment by node type

        :parameter segment:
        :return:
        """

        if segment.node2.t is SOMA:
            color = self.soma_color
        elif segment.node2.t is AXON:
            color = self.axon_color
        elif segment.node2.t is BASAL_DENDRITE:
            color = self.basal_dendrite_color
        elif segment.node2.t is APICAL_DENDRITE:
            color = self.apical_dendrite_color
        else:
            raise RuntimeError("Unrecognized node type (%s)" % segment.node2)

        return color

    def __set_segment_dimensions(self, xoffset, width, segment, scale):

        low = 0
        high = 0

        x0 = xoffset + width / 2 + scale * segment.node1.x
        y0 = -scale * segment.node1.y
        x1 = xoffset + width / 2 + scale * segment.node2.x
        y1 = -scale * segment.node2.y

        if x0 < 0:
            low = min(low, x0)
        if x1 < 0:
            low = min(low, x1)
        if x0 >= width:
            high = max(high, x0)
        if x1 >= width:
            high = max(high, x1)

        dimensions = (x0, y0, x1, y1)

        return dimensions

    def __draw_scalebar(self, draw, morphology_top, morphology_bottom, histogram_top, histogram_bottom, histogram_left,
                        reference_line, color=DEFAULT_SCALE_BAR_COLOR):

        draw.line((histogram_left, histogram_top, reference_line, morphology_top), color)
        draw.line((histogram_left, histogram_bottom, reference_line, morphology_bottom), color)
        draw.line((reference_line, morphology_top, reference_line, morphology_bottom), color)

    def __draw_cortex_thumbnail(self, draw, width, height, xoffset, pia_transform, line_color=DEFAULT_LINE_COLOR):

        scale = self.__set_scale(height)
        nrn_transform = self.__transform_swc_to_pia_space(pia_transform)
        morphology_dimensions = self.morphology.get_dimensions()
        print nrn_transform
        if self.DRAW_AXON_FIRST:
            for segment in nrn_transform.compartment_list:

                color = self.__set_color_by_node_type(segment)
                #draw.line(dimensions, color)

    def draw_cell_thumbnail(self, draw, width, height, xoffset, pia_transform):

        nrn_transform = self.__transform_swc_to_pia_space(pia_transform)
        soma = nrn_transform.soma_root()
        min_x = soma.x
        max_x = soma.x
        min_y = soma.y
        max_y = soma.y

        INSET = 4

        for node in nrn_transform.node_list:
            max_x = max(max_x, node.x)
            min_x = min(min_x, node.x)
            max_y = max(max_y, node.y)
            min_y = min(min_y, node.y)
        scale_x = (width - 2 * INSET) / (max_x - min_x + 1)
        scale_y = (height - 2 * INSET) / (max_y - min_y + 1)
        scale = min(scale_x, scale_y)

        in_x = width / 2 - scale * (max_x - min_x) / 2
        in_y = height / 2 - scale * (max_y - min_y) / 2

        for seg in nrn_transform.compartment_list:
            if self.DRAW_AXON_FIRST and seg.node2.t != 2:
                continue
            # determine drawing color
            if seg.node2.t == 1:
                col = self.soma_color
            elif seg.node2.t == 2:
                col = self.axon_color
            elif seg.node2.t == 3:
                col = self.basal_dendrite_color
            elif seg.node2.t == 4:
                col = self.apical_dendrite_color
            else:
                raise RuntimeError("Unrecognized node type (%s)" % seg.node2)
            x0 = xoffset + in_x + scale * (seg.node1.x - min_x)
            y0 = height - in_y - scale * (seg.node1.y - min_y)
            x1 = xoffset + in_x + scale * (seg.node2.x - min_x)
            y1 = height - in_y - scale * (seg.node2.y - min_y)
            draw.line((x0, y0, x1, y1), col)
        soma_line_x = xoffset + in_x + scale * (soma.x - min_x)

        if self.DRAW_AXON_FIRST:
            for seg in nrn_transform.compartment_list:
                if seg.node2.t == 2:
                    continue
                # determine drawing color
                if seg.node2.t == 1:
                    col = self.soma_color
                elif seg.node2.t == 2:
                    col = self.axon_color
                elif seg.node2.t == 3:
                    col = self.basal_dendrite_color
                elif seg.node2.t == 4:
                    col = self.apical_dendrite_color
                else:
                    raise RuntimeError("Unrecognized node type (%s)" % seg.node2)
                x0 = xoffset + in_x + scale * (seg.node1.x - min_x)
                y0 = height - in_y - scale * (seg.node1.y - min_y)
                x1 = xoffset + in_x + scale * (seg.node2.x - min_x)
                y1 = height - in_y - scale * (seg.node2.y - min_y)
                draw.line((x0, y0, x1, y1), col)
        return in_y, soma_line_x

    def draw_density(self, draw, width, height, xoffset, pia_transform):

        scale = self.__set_scale(height)

        nrn_transform = self.__transform_swc_to_pia_space(pia_transform)

        hist_2 = np.zeros(height)
        hist_3 = np.zeros(height)
        hist_4 = np.zeros(height)
        hist = np.zeros(height)
        top = 0
        bottom = height
        # for each compartment, split its length (weight) between bins for
        #   start and end nodes
        for seg in nrn_transform.compartment_list:
            wt = seg.length / 2.0
            # node 1
            bin1 = int(-scale * seg.node1.y)
            # only include parts of the histogram that are in the viewable
            #   range (ie, exclude parts that extend to pia and/or wm)
            if bin1 < height and bin1 >= 0:
                if seg.node1.t == 2:
                    hist_2[bin1] += wt
                elif seg.node1.t == 3:
                    hist_3[bin1] += wt
                elif seg.node1.t == 4:
                    hist_4[bin1] += wt
                hist[bin1] += wt
                bottom = min(bin1, bottom)
                top = max(bin1, top)
            # node 2
            bin2 = int(-scale * seg.node2.y)
            if bin2 < height and bin2 >= 0:
                if seg.node2.t == 2:
                    hist_2[bin2] += wt
                elif seg.node2.t == 3:
                    hist_3[bin2] += wt
                elif seg.node2.t == 4:
                    hist_4[bin2] += wt
                hist[bin2] += wt
                bottom = min(bin2, bottom)
                top = max(bin2, top)
        hist_scale = (width - 1) / hist.max()
        # draw axis line
        col = (128, 128, 128, 255)
        draw.line((xoffset, 0, xoffset, height), col)

        histogram_top = None
        histogram_bottom = None
        for i in range(height):
            x0 = 1 + xoffset
            x1 = 1 + xoffset + int(hist_2[i] * hist_scale + 0.99)
            if x0 != x1:
                draw.line((int(x0), i, int(x1), i), self.axon_color)
                if not histogram_top:
                    histogram_top = i
                histogram_bottom = i
            x0 = x1
            x1 += int(hist_3[i] * hist_scale + 0.99)
            if x0 != x1:
                draw.line((x0, i, x1, i), self.dendrite_color)
                if not histogram_top:
                    histogram_top = i
                histogram_bottom = i
            x0 = x1
            x1 += int(hist_4[i] * hist_scale + 0.99)
            if x0 < x1:
                draw.line((x0, i, x1, i), self.apical_color)
                if not histogram_top:
                    histogram_top = i
                histogram_bottom = i
        return histogram_top, histogram_bottom

    def _draw_layer_boundries(self, draw, height, cell_width, histogram_width,
                              layer_boundaries_color=DEFAULT_LAYER_BOUNDARIES_COLOR):

        total_width = cell_width + histogram_width
        draw.line((cell_width, 0, total_width, 0), layer_boundaries_color)
        draw.line((cell_width, height / 5, total_width, height / 5), self.layer_boundaries_color)
        draw.line((cell_width, 2 * height / 5, total_width, 2 * height / 5), self.layer_boundaries_color)
        draw.line((cell_width, 3 * height / 5, total_width, 3 * height / 5), self.layer_boundaries_color)
        draw.line((cell_width, 4 * height / 5, total_width, 4 * height / 5), self.layer_boundaries_color)
        draw.line((cell_width, height - 1, total_width, height - 1), self.layer_boundaries_color)

    def test_draw_cortex_thumbnail(self, img, cortex_width, cortex_height, xoffset, pia_transform):

        draw = ImageDraw.Draw(img)
        low, high = self.__draw_cortex_thumbnail(draw, cortex_width, cortex_height, xoffset, pia_transform)
        # make image variable width
        sz = max(-low, high)
        img = Image.new("RGBA", (cortex_width + int(2 * sz), cortex_height))
        draw = ImageDraw.Draw(img)
        self.__draw_cortex_thumbnail(draw, cortex_width + 2 * sz, cortex_height, xoffset, pia_transform)

    def draw_cortex_thumbnail(self, img, cortex_width, cortex_height, xoffset, pia_transform):

        draw = ImageDraw.Draw(img)
        self.__draw_cortex_thumbnail(draw, cortex_width, cortex_height, xoffset, pia_transform)

    def draw_thumbnail(self, img, cell_width, height, histogram_width, pia_transform, offset, scalebar=True):

        draw = ImageDraw.Draw(img)

        in_y, soma_line_x = self.draw_cell_thumbnail(draw, cell_width, height, offset, pia_transform)
        self._draw_layer_boundries(draw, height, cell_width, histogram_width)
        histogram_top, histogram_bottom = self.draw_density(draw, histogram_width, height, cell_width, pia_transform)
        if scalebar:
            self.__draw_scalebar(draw, in_y, height - in_y, histogram_top, histogram_bottom, cell_width, soma_line_x)
