"""CLI schemas for the inputs to and outputs from snap_polygons.
"""
from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    Nested, String, List, Float, InputFile, OutputFile, Int)


class SimpleGeometry(DefaultSchema):
    """A named planar geometry
    """

    name = String(
        description="identifier for this layer", 
        required=True
    )
    path = List(
        List(Float),
        description=(
            "Coordinates defining this geometric object as [[x, y], [x, y]]"
        ),
        required=True
    )


class Image(DefaultSchema):
    """A specification for a diagnostic overlay image
    """

    input_path = InputFile(
        description="Read the image from here",
        required=True
    )
    output_path = OutputFile(
        description="Write outputs to (siblings of) this path",
        required=True
    )
    downsample = Int(
        description=(
            "Downsample the image by this amount on each dimension "
            "(currently this is just a decimation, hence Int)."
        ),
        required=True,
        default=8
    )
    overlay_types = List(
        String,
        description=(
            "produce these types of overlays for this image. "
            "See ImageOutputter for options"
        ),
        required=True,
        default=["before", "after"]
    )


class InputParameters(ArgSchema):
    """Top-level schema for inputs to snap_polygons
    """

    layer_polygons = Nested(
        SimpleGeometry,
        description=(
            "Each entry defines the entire (simple) boundary of a layer"
        ),
        many=True,
        required=True
    )
    pia_surface = Nested(
        SimpleGeometry,
        description="A path defining the pia-side surface of the cortex",
        required=True
    )
    wm_surface = Nested(
        SimpleGeometry,
        description=(
            "A path defining the white matter-side surface of the cortex"
        ),
        required=True
    )
    working_scale = Float(
        description=(
            "When computing close-fitting boundaries, do so in a raster "
            "space scaled from the inputs according to this value."),
        required=False,
        default=1.0 / 4
    )
    images = Nested(
        Image,
        description=(
            "Each defines an image (in the space of the geometric objects) on "
            "which overlays will be drawn"
        ),
        required=False,
        many=True
    )
    layer_order = List(
        String,
        description=(
            "Layer polygons will be ordered according to this rule when "
            "finding inter-layer surfaces. Names not in this list will not be "
            "ordered, but not all names in this list need to be present."
        ),
        required=True,
        default=[
            "Layer1", 
            "Layer2", 
            "Layer2/3",
            "Layer3",
            "Layer4",
            "Layer5",
            "Layer6a",
            "Layer6",
            "Layer6b"    
        ]
    )
    surface_distance_threshold = Float(
        description=(
            "Pia and white matter surfaces that extend farther from the layer "
            "polygons than this value will be cut off. Units should match "
            "surfaces and layer polygons"
        ),
        default=400.0,
        required=True
    )
    multipolygon_error_threshold = Float(
        description=(
            "If an intermediate stage cuts an obtained polygon into multiple "
            "components, we reject all but the largest by area. This is fine "
            "when there is a clear main polygon, but less so when there are "
            "several of similar size. Therefore, we reject the largest "
            "polygon unless its area is at least this many times the second "
            "largest's."
        ),
        default=10**4,
        required=True
    )


class OutputImage(DefaultSchema):
    """Metadata describing an output diagnoctic overlay image.
    """

    input_path = InputFile(
        description="The base image was read from here",
        required=True
    )
    output_path = OutputFile(
        description="The overlay was written to here",
        required=True
    )
    downsample = Int(
        description=(
            "The base image was downsampled by this factor along each axis"
        ),
        required=True,
    )
    overlay_type = String(
        description="This image has this kind of overlay",
        required=True,
    )


class OutputParameters(DefaultSchema):
    """Top-level schema for snap_polygons outputs.
    """

    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    polygons = Nested(
        SimpleGeometry,
        description="The close boundary found for each layer",
        many=True,
        required=True
    )
    surfaces = Nested(
        SimpleGeometry,
        description="The pia and white matter side inter-layer boundaries",
        many=True,
        required=True
    )
    images = Nested(
        OutputImage,
        description="Records of each overlay generated",
        required=False,
        many=True
    )
