from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, List, Float, Int, Nested
)


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description=(
            "File at this location defines the morphology whose upright angle "
            "will be calculated"
        ),
        required=True
    )
    gradient_path = InputFile(
        description=(
            "File at this location is a netcdf-formatted 2D gradient field."
            "Dimensions are x, y, dim, where dim defines the component (dx "
            "or dy) of the gradient"
        ),
        required=True
    )
    decimate = Int(
        description=(
            "The input gradient field will be decimated isometrically by "
            "this factor"
        ),
        default=10
    )


class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    angle = Float(
        description=(
            "Angle of rotation about the soma required to upright the input "
            "morphology. In radians counterclockwise from horizontal axis"
        ),
        required=True
    )
    transform = List(
        List(Float),
        description=(
            "2D affine transform which, when applied to the coordinates of a "
            "morphological node (in x, y order), uprights that node."
        ),
        required=True
    )