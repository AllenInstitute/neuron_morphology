from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    Nested, String, List, Float, InputFile, OutputFile, Int)


class SimpleGeometry(DefaultSchema):
    name = String(descripion="identifier for this layer")
    path = List(
        List(Float),
        description="",
        required=True
    )

class ImageDimensions(DefaultSchema):
    width = Float(
        description="",
        required=True
    )
    height = Float(
        description="",
        required=True
    )

class TwodAffine(DefaultSchema):
    hh = Float(description="")
    hv = Float(description="")
    vh = Float(description="")
    vv = Float(description="")
    htr = Float(description="")
    vtr = Float(description="")

class Image(DefaultSchema):
    input_path = InputFile(
        description="",
        required=True
    )
    output_path = OutputFile(
        description="",
        required=True
    )
    transform = Nested(
        TwodAffine,
        description="",
        required=False
    )

class InputParameters(ArgSchema):
    layer_polygons = Nested(
        SimpleGeometry,
        description="",
        many=True,
        required=True
    )
    pia_surface = Nested(
        SimpleGeometry,
        description="",
        required=True
    )
    wm_surface = Nested(
        SimpleGeometry,
        description="",
        required=True
    )
    image_dimensions = Nested(
        ImageDimensions,
        description="",
        required=True
    )
    working_scale = Float(
        description="",
        required=False,
        default=1.0 / 8
    )
    images = Nested(
        Image,
        description="",
        required=False,
        many=True
    )


class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    layer_polygons = Nested(
        SimpleGeometry,
        description="",
        many=True,
        required=True
    )
    pia_surfaces = Nested(
        SimpleGeometry,
        description="",
        many=True,
        required=True
    )
    images = Nested(
        Image,
        description="",
        required=False,
        many=True
    )