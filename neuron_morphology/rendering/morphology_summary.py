from neuron_morphology.constants import *
import neuron_morphology.rendering.colors as co
from PIL import ImageDraw, Image
import numpy as np
from collections import defaultdict


class MorphologySummary(object):

    """ Class to create thumbnails for neuron reconstructions

    Parameters
    ----------

    morphology: Morphology object
        Object created from an swc file that is being drawn

    pia_transform: dict
        Transformation matrix data organized as a json

    width: int
        Width of the morphology summary image area

    height: int
        Height of the morphology summary image area

    ordered_node_types: list of int
        List of node types that decides the order of drawing

    colors: Colors object
        Colors used to draw the morphology summary
    """

    def __init__(self, morphology, pia_transform, width, height, ordered_node_types, colors=co.Colors()):

        self._pia_transform = pia_transform
        self._morphology = self._transform_swc_to_pia_space(morphology)
        self._width = int(width)
        self._height = int(height)
        self._ordered_node_types = ordered_node_types
        self._colors = colors

    @property
    def colors(self):
        return self._colors

    @property
    def morphology(self):
        return self._morphology

    def _create_affine_matrix(self):

        # construct affine transform
        affine = np.zeros(9)
        for i in range(9):
            affine[i] = self._pia_transform["tvr_%02d" % i]

        matrix = affine.reshape(3, 3)
        tx = self._pia_transform["tvr_09"]
        ty = self._pia_transform["tvr_10"]
        tz = self._pia_transform["tvr_11"]
        translation_matrix = np.vstack((tx, ty, tz))
        new_matrix = np.hstack((matrix, translation_matrix))
        zeros_and_ones = np.hstack((0, 0, 0, 1))
        affine = np.vstack((new_matrix, zeros_and_ones))

        return affine

    def _transform_swc_to_pia_space(self, morphology):

        """ Transforms the morphology to pia space

            Parameters
            ----------

            morphology: Morphology object


            Returns
            -------

            nrn_clone: Morphology object
                Morphology object that is transformed to pia space

        """

        affine = self._create_affine_matrix()

        # draw compartments
        # order them by depth to approximate 3D rendering
        sorted(morphology.get_compartments(), key=lambda x: x[0]['y'])

        # transform to pia-space
        morphology = morphology.apply_affine(affine)
        return morphology

    def calculate_scale(self):

        """ Calculates scaling factor and x,y insets required to auto-scale
            and center morphology into box with specified numbers of pixels

            Parameters
            ----------

            Returns
            -------

            scale_factor: double
                Scaling factor

            scale_inset_x: double
                Number of pixels needed to adjust x-coordinates so that the
                morphology is horizontally centered

            scale_inset_y: double
                Number of pixels needed to adjust the y-coordinates so that
                the morphology is vertically centered
                .
        """

        dims, low, high = self._morphology.get_dimensions()

        # get boundaries of morphology
        xlow = low[0]
        xhigh = high[0]
        ylow = low[1]
        yhigh = high[1]

        # determine scale on X and Y to make morphology fit in image area
        try:
            horizontal_scale = self._width / (xhigh - xlow)
        except ZeroDivisionError:
            horizontal_scale = None

        try:
            vertical_scale = self._height / (yhigh - ylow)
        except ZeroDivisionError:
            vertical_scale = None

        # select lowest scaling factor so morphology is stretched to
        #   maximum width/height along axis that is tightest fit
        if horizontal_scale is None or vertical_scale is None:
            scale_factor = 1.0
            scale_inset_x = 0.0
            scale_inset_y = 0.0

        elif horizontal_scale < vertical_scale:
            scale_factor = horizontal_scale
            # center image vertically
            morphology_vertical_center = (ylow + yhigh) / 2.0
            scale_inset_x = -xlow * scale_factor
            # invert y coordinates for conversion to pixel space
            scale_inset_y = (self._height / 2.0) + (scale_factor * morphology_vertical_center)
        else:
            scale_factor = vertical_scale
            # center image horizontally
            morphology_horizontal_center = (xlow + xhigh) / 2.0
            scale_inset_x = (self._width / 2.0) - (scale_factor * morphology_horizontal_center)
            # morphology is upside down, so the bottom on the y axis is
            #   the high value there (ie, use yhigh instead of ylow)
            scale_inset_y = yhigh * scale_factor
        return scale_factor, scale_inset_x, scale_inset_y

    def _convert_x_value_to_pixel(self, x_value, scale_factor, scale_inset_x):

        """ Converts the nodes' x value to pixel

            Parameters
            ----------

            x_value: double
                Node's x value

            scale_factor: double
                Scaling factor

            scale_inset_x: double
                Number of pixels needed to adjust x-coordinates so that the
                morphology is horizontally centered

            Returns
            -------

            Node's horizontal position in the image

        """

        return scale_inset_x + scale_factor * x_value

    def _convert_y_value_to_pixel(self, y_value, scale_factor, scale_inset_y):

        """ Converts the nodes' y value to pixel

            Parameters
            ----------

            y_value: double
                Node's y value

            scale_factor: double
                Scaling factor

            scale_inset_y: double
                Number of pixels needed to adjust the y-coordinates so that
                the morphology is vertically centered

            Returns
            -------

            Node's vertical position in the image

        """

        return scale_inset_y - scale_factor * y_value

    def top(self):

        """ Calculates vertical location of the top of the morphology

            Parameters
            ----------


            Returns
            -------

            Y value of the location of the top of the morphology

        """

        dims, low, high = self._morphology.get_dimensions()
        scale_factor, scale_inset_x, scale_inset_y = self.calculate_scale()
        return self._convert_y_value_to_pixel(high[1], scale_factor, scale_inset_y)

    def bottom(self):

        """ Calculates the vertical location of the bottom of the morphology

            Parameters
            ----------


            Returns
            -------

            Y value of the location of the bottom of the morphology

        """

        dims, low, high = self._morphology.get_dimensions()
        scale_factor, scale_inset_x, scale_inset_y = self.calculate_scale()
        return self._convert_y_value_to_pixel(low[1], scale_factor, scale_inset_y)

    def draw_morphology_summary(self):

        """ Draws the morphology in the defined space

            Parameters
            ----------

            Returns
            -------

            img: PIL Image
                Image of the morphology summary

        """

        scale_factor, scale_inset_x, scale_inset_y = self.calculate_scale()

        img = Image.new("RGBA", (self._width, self._height))
        canvas = ImageDraw.Draw(img)

        segments_by_node_type = self._group_segments_by_node_type(self._morphology.get_compartments())

        for node_type in self._ordered_node_types:
            if node_type is SOMA:
                self._draw_morphology_soma(canvas, self._morphology, scale_factor, scale_inset_x, scale_inset_y)
            else:
                for segment in segments_by_node_type[node_type]:
                    color = self.set_color_by_node_type(segment)
                    x0 = self._convert_x_value_to_pixel(segment[0]['x'], scale_factor, scale_inset_x)
                    y0 = self._convert_y_value_to_pixel(segment[0]['y'], scale_factor, scale_inset_y)
                    x1 = self._convert_x_value_to_pixel(segment[1]['x'], scale_factor, scale_inset_x)
                    y1 = self._convert_y_value_to_pixel(segment[1]['y'], scale_factor, scale_inset_y)
                    canvas.line((x0, y0, x1, y1), color)

        return img

    def _group_segments_by_node_type(self, segments):

        """ Draws the morphology in the defined space

            Parameters
            ----------

            segments: list of Segments


            Returns
            -------

            segments_by_node_type: defaultdict

        """

        segments_by_node_type = defaultdict(list)
        for segment in segments:
            node_type = segment[1]['type']
            segments_by_node_type[node_type].append(segment)
        return segments_by_node_type

    def set_color_by_node_type(self, segment):

        """ Draws the morphology in the defined space

            Parameters
            ----------

            segment: Segment object


            Returns
            -------

            color: tuple

        """

        node2_type = segment[1]['type']

        if node2_type == AXON:
            color = self._colors.axon_color
        elif node2_type == BASAL_DENDRITE:
            color = self._colors.basal_dendrite_color
        elif node2_type == APICAL_DENDRITE:
            color = self._colors.apical_dendrite_color
        else:
            raise RuntimeError("Unrecognized node type (%s)" % segment[1])

        return color

    def _draw_morphology_soma(self, canvas, morphology, scale_factor, scale_inset_x, scale_inset_y):

        """ Draws the morphology soma in the defined space

            Parameters
            ----------

            canvas:

            morphology: Morphology object

            scale_factor: double
                Scaling factor

            scale_inset_x: double
                Number of pixels needed to adjust x-coordinates so that the
                morphology is horizontally centered

            scale_inset_y: double
                Number of pixels needed to adjust the y-coordinates so that
                the morphology is vertically centered.

        """

        root = morphology.get_root()

        if root:
            x = self._convert_x_value_to_pixel(root['x'], scale_factor, scale_inset_x)
            y = self._convert_y_value_to_pixel(root['y'], scale_factor, scale_inset_y)
            radius = scale_factor * root['radius']
            x0 = int(x - radius)
            y0 = int(y - radius)
            x1 = int(x0 + 2 * radius)
            y1 = int(y0 + 2 * radius)
            canvas.ellipse((x0, y0, x1, y1), fill=self._colors.soma_color, outline=self._colors.soma_color)
