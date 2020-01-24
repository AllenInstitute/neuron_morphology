from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, OutputFile, String, Nested, Dict, List, Int, Field, Float)
from marshmallow import ValidationError


class Transform(DefaultSchema):
    descent_field_path = InputFile(
        description=(
            "The path to an xarray file describing the gradient of cortical "
            "depth on some domain. This file should contain one dataarray "
            "called 'gradient' which has dimensions drawn from "
            "{'x', 'y', 'z', 'component'}. The coords of x, y, z define the "
            "domain over which the gradient was computed. The component "
            "dimension describes the dimension associated with each component "
            "of the gradient and should have coords drawn from {'x', 'y', 'z'}."
        ),
        required=False
    )

    @classmethod
    def is_valid(cls, value):
        pass


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description="path to input swc (csv) file", 
        required=True
    )
    transform = Transform(
        description=(
            "A transform specified which can be evaluated at the "
            "location of each node in the input swc"
        ),
        required=True,
        validate=Transform.is_valid
    )

class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
