from PIL import Image, ImageDraw
import numpy as np


class MorphologyColors(object):
    def __init__(self):
        self.soma = (0, 0, 0)
        self.axon = (70, 130, 180)
        self.axon_disconnected = (192, 192, 192)
        self.basal = (178, 34, 34)
        self.apical = (255, 127, 80)

    def set_soma_color(self, r, g, b):
        self.soma = (r, g, b)

    def set_axon_color(self, r, g, b):
        self.axon = (r, g, b)

    def set_disconnected_axon_color(self, r, g, b):
        self.axon_disconnected = (r, g, b)

    def set_basal_color(self, r, g, b):
        self.basal = (r, g, b)

    def set_apical_color(self, r, g, b):
        self.apical = (r, g, b)


# create empty image
def create_image(w, h, color=None, alpha=False):
    if alpha:
        mode = 'RGBA'
    else:
        mode = 'RGB'
    if color is not None:
        return Image.new(mode, (w,h), color)
    else:
        if mode == 'RGBA':
            return Image.new(mode, (w,h), (0, 0, 0, 0))
        else:
            return Image.new(mode, (w,h), (0, 0, 0))


def calculate_scale(morph, pix_width, pix_height):
    """ Calculates scaling factor and x,y insets required to auto-scale
        and center morphology into box with specified numbers of pixels

        Parameters
        ----------

        morph: AISDK Morphology object

        pix_width: int
        Number of image pixels on X axis

        pix_height: int
        Number of image pixels on Y axis

        Returns
        -------
        real, real, real
        First return value is the scaling factor. Second is the
        number of pixels needed to adjust x-coordinates so that the
        morphology is horizontally centered. Third is the number of 
        pixels needed to adjust the y-coordinates so that the morphology 
        is vertically centered.
    """
    dims, low, high = morph.get_dimensions()
    # get boundaries of morphology
    xlow = low[0]
    xhigh = high[0]
    ylow = low[1]
    yhigh = high[1]
    # determine scale on X and Y to make morphology fit in image area
    hscale = pix_width / (xhigh - xlow)
    vscale = pix_height / (yhigh - ylow)
    # select lowest scaling factor so morphology is stretched to
    #   maximum width/height along axis that is tightest fit
    #   and adjust inset on other axis so morphology is centered
    # also set inset values appropriately
    if hscale < vscale:
        # image constrained on horizontal axis
        scale_factor = hscale
        # center image vertically
        v_center = (ylow + yhigh) / 2.0
        scale_inset_x = -low[0] * scale_factor
        # invert y coordinates for conversion to pixel space
        scale_inset_y = pix_height/2 + scale_factor*v_center
    else:
        # image constrained on vertical axis
        scale_factor = vscale
        # center image horizontally
        h_center = (xlow + xhigh) / 2.0
        scale_inset_x = pix_width/2 - scale_factor*h_center
        # morphology is upside down, so the bottom on the y axis is
        #   the high value there (ie, use high[1] instead of low[1])
        scale_inset_y = high[1] * scale_factor
    return scale_factor, scale_inset_x, scale_inset_y


# draw morphology on image -- takes image and morphology, modifies image
#       options: scale to fit | linear scaling
def draw_morphology(img, morph, 
        inset_left=0, inset_right=0, inset_top=0, inset_bottom=0, 
        scale_to_fit=False, scale_factor=1.0, colors=None):
    """ Draws morphology onto image
        When no scaling is applied, and no insets are provided, the 
        coordinates of the morphology are used directly -- i.e., 100 in
        morphology coordinates is equal to 100 pixels.

        The scale factor is multiplied to morphology coordinates before
        being drawn. If scale_factor=2 then 50 in morphology coordinates
        is 100 pixels. Left and top insets shift the coordinate axes
        for drawing. E.g., if left=10 and top=5 then 0,0 in morphology
        coordinates is 10,5 in pixel space. Bottom and right insets are
        ignored.
        
        If scale_to_fit is set then scale factor is ignored. The 
        morphology is scaled to be the maximum size that fits in
        the image, taking into account insets. In a 100x100 image, if
        all insets=10, then the image is scaled to fit into the center
        80x80 pixel area, and nothing is drawn in the inset border areas.

        Axons are drawn before soma and dendrite compartments.


        Parameters
        ----------
        
        img: PIL image object

        morph: AISDK Morphology object

        inset_*: real
        This is the number of pixels to use as border on top/bottom/
        right/left. If scale_to_fit is false then only the top/left
        values are used, as the scale_factor will determine how
        large the morphology is (it can be drawn beyond insets and even
        beyond image boundaries)

        scale_to_fit: boolean
        If true then morphology is scaled to the inset area of the 
        image and scale_factor is ignored. Morphology is centered
        in the image in the sense that the top/bottom and left/right
        edges of the morphology are equidistant from image borders.

        scale_factor: real
        A scalar amount that is multiplied to morphology coordinates
        before drawing

        colors: MorphologyColors object
        This is the color scheme used to draw the morphology. If 
        colors=None then default coloring is used

        Returns
        -------

        2-dimensional array, the pixel coordinates of the soma root [x,y]
    """
    # determine drawing area, scaling factor, offset to origin
    # if scaling to fit, find value that scales morphology so height
    #   or width matches image area. adjust scale_factor and insets
    #   as necessary so morphology can be drawn normally
    dims, low, high = morph.get_dimensions()
    if scale_to_fit:
        # get image area based on requested insets
        width, height = img.size
        pix_width = (width - inset_right) - inset_left
        pix_height = (height - inset_bottom) - inset_top
        # get scale and x,y insets from auto-scaling
        scale_factor, scale_inset_x, scale_inset_y = calculate_scale(morph, pix_width, pix_height)
    else:
        # no implicit inset necessary due to scaling
        scale_inset_x = 0
        scale_inset_y = 0

    # order compartments by depth to approximate 3D rendering
    sorted(morph.compartment_list, key=lambda x: x.node1.y)

    # if color not specified, select default
    if colors is None:
        colors = MorphologyColors()

    canvas = ImageDraw.Draw(img)

    for i in range(4):
        for comp in morph.compartment_list:
            color = None
            if comp.node2.t == 1:
                if i == 3: # soma drawn last
                    # NOTE: there are unlikely to be soma compartments
                    # additional soma-drawing code is below
                    color = colors.soma
            elif comp.node2.t == 2:
                # axon drawn first
                if i == 0 and comp.node2.tree_id != 0:
                    color = colors.axon_disconnected
                elif i == 1 and comp.node2.tree_id == 0:
                    color = colors.axon
            elif comp.node2.t == 3:
                if i == 2: # dendrite drawn second
                    color = colors.basal
            elif comp.node2.t == 4:
                if i == 2: # dendrite drawn second
                    color = colors.apical
            if color is None:
                continue
            x0 = scale_inset_x + inset_left + scale_factor * comp.node1.x
            x1 = scale_inset_x + inset_left + scale_factor * comp.node2.x
            # y coordinate inverted because morphology values are
            #   increasing going 'up while pixel values increase
            #   going down
            y0 = scale_inset_y + inset_top - scale_factor * comp.node1.y
            y1 = scale_inset_y + inset_top - scale_factor * comp.node2.y
            canvas.line((x0, y0, x1, y1), color)

    # a compartment type is defined by the type of the 2nd node defining
    #   the compartment. if there is a single soma node, there can be
    #   no soma compartments. draw the root soma node
    root = morph.soma_root()
    x = scale_inset_x + inset_left + scale_factor * root.x
    y = scale_inset_y + inset_top - scale_factor * root.y
    rad = scale_factor * root.radius
    x0 = int(x - rad)
    y0 = int(y - rad)
    x1 = int(x0 + 2*rad)
    y1 = int(y0 + 2*rad)
    canvas.ellipse((x0,y0,x1,y1), fill=colors.soma, outline=colors.soma)

    # return soma root coordinate, in unit of pixels
    return [x, y]


def draw_density_hist(img, morph, vert_scale,
        inset_left=0, inset_right=0, inset_top=0, inset_bottom=0, 
        num_bins=None, colors=None, bin_max=None):
    """ Draws density histogram onto image
        When no scaling is applied, and no insets are provided, the 
        coordinates of the morphology are used directly -- i.e., 100 in
        morphology coordinates is equal to 100 pixels.

        The scale factor is multiplied to morphology coordinates before
        being drawn. If scale_factor=2 then 50 in morphology coordinates
        is 100 pixels. Left and top insets shift the coordinate axes
        for drawing. E.g., if left=10 and top=5 then 0,0 in morphology
        coordinates is 10,5 in pixel space. Bottom and right insets are
        ignored.
        
        If scale_to_fit is set then scale factor is ignored. The 
        morphology is scaled to be the maximum size that fits in
        the image, taking into account insets. In a 100x100 image, if
        all insets=10, then the image is scaled to fit into the center
        80x80 pixel area, and nothing is drawn in the inset border areas.

        Axons are drawn before soma and dendrite compartments.


        Parameters
        ----------
        
        img: PIL image object

        morph: AISDK Morphology object

        vert_scale: real
        This is the amout required to multiply to a moprhology
        y-coordinate to convert it to relative cortical depth (on [0,1]).
        This is the inverse of the cortical thickness.

        inset_*: real
        This is the number of pixels to use as border on top/bottom/
        right/left. If scale_to_fit is false then only the top/left
        values are used, as the scale_factor will determine how
        large the morphology is (it can be drawn beyond insets and even
        beyond image boundaries)

        num_bins: int
        The number of bins in the histogram

        colors: MorphologyColors object
        This is the color scheme used to draw the morphology. If 
        colors=None then default coloring is used

        bin_max: int
        Auto-scaling feature. This is the number of elements in a bin
        such that the bin reaches the max histogram value (i.e., 1.0).
        Any values beyond this will be truncated.

        Returns
        -------

        Histogram arrays: [hist, hist2, hist3, hist4]
        where hist is the histgram of all neurites, and hist[234] are
        the histograms of SWC types 2,3,4
    """
    # if number of bins not specified, default to vertical size of 
    #   drawing area in image
    img_width, img_height = img.size
    draw_width = img_width - (inset_left + inset_right)
    draw_height = img_height - (inset_top + inset_bottom)
    if num_bins is None:
        num_bins = draw_height
    # histograms for each analyzed SWC type
    hist_2 = np.zeros(num_bins)
    hist_3 = np.zeros(num_bins)
    hist_4 = np.zeros(num_bins)
    # total response in a bin
    hist = np.zeros(num_bins)

    # if color not specified, select default
    if colors is None:
        colors = MorphologyColors()

    canvas = ImageDraw.Draw(img)

    # for each compartment, split its length (weight) between bins for 
    #   start and end nodes
    for seg in morph.compartment_list:
        wt = seg.length / 2.0
        # node 1
        bin1 = int(-vert_scale * seg.node1.y * num_bins)
        if bin1 == num_bins:
            bin1 = num_bins-1
        # only include parts of the histogram that are in the viewable
        #   range (ie, exclude parts that extend to pia and/or wm)
        if bin1 >= 0 and bin1 < num_bins:
            if seg.node1.t == 2:
                hist_2[bin1] += wt
                # omot axon from histogram display
                #hist[bin1] += wt
            elif seg.node1.t == 3:
                hist_3[bin1] += wt
                hist[bin1] += wt
            elif seg.node1.t == 4:
                hist_4[bin1] += wt
                hist[bin1] += wt
        # node 2
        bin2 = int(-vert_scale * seg.node1.y * num_bins)
        if bin2 == num_bins:
            bin2 = num_bins-1
        if bin2 >= 0 and bin2 < num_bins:
            # omit axon from histogram
            if seg.node2.t == 2:
                hist_2[bin2] += wt
                # omot axon from histogram display
                #hist[bin2] += wt
            elif seg.node2.t == 3:
                hist_3[bin2] += wt
                hist[bin2] += wt
            elif seg.node2.t == 4:
                hist_4[bin2] += wt
                hist[bin2] += wt
    
    # draw axis line
    col = (128, 128, 128, 256)
    x0 = inset_left
    x1 = x0
    y0 = inset_top
    y1 = img_height-inset_bottom
    canvas.line((x0, y0, x1, y1), col)

    hist_step = 1.0 * draw_height / num_bins;
    if bin_max is not None and bin_max > 0:
        hist_scale = 1.0 * (draw_width-1) / bin_max
    else:
        hist_scale = (draw_width-1) / hist.max()
    for seg in morph.compartment_list:
        ypos = 1.0 * inset_top
        for i in range(num_bins):
            y0 = int(ypos)
            y1 = int(ypos + hist_step)
            x0 = int(1 + inset_left)
            # omit axon from histogram drawing
            x1 = x0
            #x1 = int(1 + inset_left + hist_2[i] * hist_scale + 0.99)
            #if x0 != x1:
            #    ytmp = ypos
            #    while ytmp < y1:
            #        canvas.line((x0, int(ytmp), x1, int(ytmp)), colors.axon)
            #        ytmp += hist_step
            x0 = x1
            x1 += int(hist_3[i] * hist_scale + 0.99)
            if x1 > inset_left + draw_width:
                x1 = inset_left + draw_width
            if x0 != x1:
                ytmp = ypos
                while ytmp < y1:
                    canvas.line((x0, int(ytmp), x1, int(ytmp)), colors.basal)
                    ytmp += hist_step
            x0 = x1
            x1 += int(hist_4[i] * hist_scale + 0.99)
            if x1 > inset_left + draw_width:
                x1 = inset_left + draw_width
            if x0 < x1:
                ytmp = ypos
                while ytmp < y1:
                    canvas.line((x0, int(ytmp), x1, int(ytmp)), colors.apical)
                    ytmp += hist_step
            ypos += hist_step

    return hist, hist_2, hist_3, hist_4


def draw_morphology_2(img, morph, 
        inset_left=0, inset_right=0, inset_top=0, inset_bottom=0, 
        scale_to_fit=False, scale_factor=1.0, colors=None):
    """ Draws morphology onto image
        The input parameters are the same as for draw_morphology()
        and the two procedures are otherwise very similar. The primary
        difference is that this procedure draws a morphology fully
        depth-first (the standard procedure draws axons before dendrites
        for clarity) and the compartments are scaled by diameter, and
        thickened a bit more for good measure.

        This procedure is meant for creating frames for rotating
        morphology movies.

        Returns
        -------
        <nothing>
    """
    # determine drawing area, scaling factor, offset to origin
    # if scaling to fit, find value that scales morphology so height
    #   or width matches image area. adjust scale_factor and insets
    #   as necessary so morphology can be drawn normally
    dims, low, high = morph.get_dimensions()
    if scale_to_fit:
        # get image area based on requested insets
        width, height = img.size
        pix_width = (width - inset_right) - inset_left
        pix_height = (height - inset_bottom) - inset_top
        # get scale and x,y insets from auto-scaling
        scale_factor, scale_inset_x, scale_inset_y = calculate_scale(morph, pix_width, pix_height)
    else:
        # no implicit inset necessary due to scaling
        scale_inset_x = 0
        scale_inset_y = 0

    # order compartments by depth to approximate 3D rendering
    sorted(morph.compartment_list, key=lambda x: x.node1.y)

    # if color not specified, select default
    if colors is None:
        colors = MorphologyColors()

    canvas = ImageDraw.Draw(img)

    for comp in morph.compartment_list:
        if comp.node1.t == 1:
            x = scale_inset_x + inset_left + scale_factor * comp.node1.x
            y = scale_inset_y + inset_top - scale_factor * comp.node1.y
            rad = scale_factor * comp.node1.radius
            x0 = int(x - rad)
            y0 = int(y - rad)
            x1 = int(x0 + 2*rad)
            y1 = int(y0 + 2*rad)
            canvas.ellipse((x0,y0,x1,y1), fill=colors.soma, outline=colors.soma)
        else:
            if comp.node2.t == 2:
                color = colors.axon
            elif comp.node2.t == 3:
                color = colors.basal
            elif comp.node2.t == 4:
                color = colors.apical
            dia = comp.node1.radius + comp.node2.radius
            x0 = scale_inset_x + inset_left + scale_factor * comp.node1.x
            x1 = scale_inset_x + inset_left + scale_factor * comp.node2.x
            # y coordinate inverted because morphology values are
            #   increasing going 'up while pixel values increase
            #   going down
            y0 = scale_inset_y + inset_top - scale_factor * comp.node1.y
            y1 = scale_inset_y + inset_top - scale_factor * comp.node2.y
            #if scale_factor * dia > 1.5:
            w = 1 + (min(1, int(scale_factor * dia + 0.5)))
            w0 = -w/2
            w1 = w + w0
            for i in range(w0, w1+1):
                canvas.line((x0, y0, x1, y1), color)
                canvas.line((x0+i, y0, x1+i, y1), color)
                canvas.line((x0, y0+i, x1, y1+i), color)


# TODO
# draw path on image -- takes image and path, modifies image
#def draw_path(img, path, color):
    # path is in units of pixels
    # foreach vertex, draw line in specified color

# refine section boundaries -- takes labeled regions and generates labeled mask
# -> need constraints on input. lookup of points is easy. categorizing
#   what pixel is part of what ask is not without expanding masks laterally

# label morphology -- takes morpholgoy and labeled mask and adds lables
#   to each compartment


########################################################################
# table with different pairs of colors to allow more easily drawing 
#   visually distinct groups of cells
color_table = None
next_color = 0

# internal procedure
def create_color_(a, b):
    col = MorphologyColors()
    col.axon = a
    col.basal = b
    col.apical = a
    return col

# internal procedure
def setup_color_table():
    global color_table;
    color_table = []
    color_table.append(create_color_((153,   0,   0), (255,  77,  77)))  # 0
    color_table.append(create_color_((153,  77,   0), (255, 166,  77)))  # 30
    color_table.append(create_color_((153, 153,   0), (229, 229,  46)))  # 60
    color_table.append(create_color_(( 77, 153,   0), (128, 230,  46)))  # 90
    color_table.append(create_color_(( 13, 128,  13), ( 25, 255,  25)))  # 120
    color_table.append(create_color_((  0, 179,  89), ( 77, 255, 166)))  # 150
    color_table.append(create_color_((  0, 153, 153), ( 46, 230, 230)))  # 180
    color_table.append(create_color_((  0,  77, 153), (177, 166, 255)))  # 210
    color_table.append(create_color_((  0,   0, 153), (102, 102, 255)))  # 240
    color_table.append(create_color_(( 77,   0, 153), (166,  77, 255)))  # 270
    color_table.append(create_color_((153,   0, 153), (255,  77, 255)))  # 300
    color_table.append(create_color_((153,   0,  77), (255,  51, 153)))  # 330
    color_table.append(create_color_((102, 102, 102), (179, 179, 179)))  # Y
    color_table.append(create_color_(( 78,  89,  30), (151, 166,  86)))  #

# returns a MorphologyColors object initialized to the next color pair
#   in the color table
def get_next_color():
    global next_color, color_table
    print "******** ", next_color
    if color_table is None or len(color_table) == 0:
        setup_color_table()
    if next_color >= len(color_table):
        next_color = 0
    col = color_table[next_color]
    next_color += 1
    return col

