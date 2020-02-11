from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    Nested, String, List, Float, InputFile, OutputFile, Int)


class SimpleGeometry(DefaultSchema):
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


class OutputImage(DefaultSchema):
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