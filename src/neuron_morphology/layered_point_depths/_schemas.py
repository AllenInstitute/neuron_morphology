from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, OutputFile, String, Nested, List, Int, Float, Bool)
from marshmallow import ValidationError


class DepthField(DefaultSchema):
    gradient_field_path = InputFile(
        description=(
            "The path to an xarray file describing the gradient of cortical "
            "depth on some domain. This file should contain one dataarray "
            "called 'gradient' which has dimensions drawn from "
            "{'x', 'y', 'z', 'component'}. The coords of x, y, z define the "
            "domain over which the gradient was computed. The component "
            "dimension describes the dimension associated with each component "
            "of the gradient and should have coords drawn from {'x', 'y', 'z'}."
        ),
        required=True
    )
    depth_field_path = InputFile(
        description=(
            "As gradient field, but gives depth values"
        ),
        required=True
    )
    soma_origin = Bool(
        description="If true, the field is centered at the soma",
        required=True,
        default=True
    )
    pia_sign = Int(
        description="which direction is the pia",
        required=True,
        default=1,
        validate = lambda val: val in {1, -1}
    )


class Layer(DefaultSchema):
    name = String(
        description="identifier for this layer",
        required=True
    )
    bounds = List(
        List(Float),
        description=(
            "exterior surface of the layer (interpreted as a closed polygon)"
            ),
        required=True
    )
    pia_surface = List(
        List(Float),
        description=(
            "pia-side surface of the layer, interpreted as a linestring"
        ),
        required=True
    )
    wm_surface = List(
        List(Float),
        description=(
            "white matter-side surface of the layer, "
            "interpreted as a linestring"
        ),
        required=True
    )


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description="path to input swc (csv) file", 
        required=True
    )
    depth = Nested(
        DepthField,
        description=(
            "A transform which can be evaluated at the "
            "location of each node in the input swc"
        ),
        required=True,
        many=False
    )
    layers = Nested(
        Layer,
        description="specification of layer bounds",
        many=True,
        required=True
    )
    step_size = Float(
        description=(
            "size of each step, in the same units as the depth field and swc"
        ),
        required=True,
        default=1.0
    )
    output_path = OutputFile(
        description="write (csv) outputs here",
        required=True
    )
    max_iter = Int(
        description="how many steps to take before giving up",
        required=True,
        default=1000
    )

class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    output_path = String(
        description="(csv) outputs written here",
        required=True
    )
