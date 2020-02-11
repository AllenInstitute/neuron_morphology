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

class Image(DefaultSchema):
    input_path = InputFile(
        description="",
        required=True
    )
    output_path = OutputFile(
        description="",
        required=True
    )
    downsample = Int(
        description="",
        required=True,
        default=8
    )
    overlay_types = List(
        String,
        description="",
        required=True,
        default=["before", "after"]
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
        default=1.0 / 4
    )
    images = Nested(
        Image,
        description="",
        required=False,
        many=True
    )
    layer_order = List(
        String,
        description="",
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
    surfaces = Nested(
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