import marshmallow as mm
from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, List, Float, Int, Nested
)
from neuron_morphology.transforms.affine_transformer._schemas import (
    AffineDictSchema
)

class InputParameters(ArgSchema):
    gradient_path = InputFile(
        description=(
            "File at this location is a netcdf-formatted 2D gradient field."
            "Dimensions are x, y, dim, where dim defines the component (dx "
            "or dy) of the gradient"
        ),
        required=True
    )
    node = List(Float,
        description='[x,y,z] location in gradient field to get angle',
        cli_as_single_argument=True,
        default=[0, 0, 0],
        required=False,
    )

    step = Int(
        description=(
            "The input gradient field will be decimated isometrically by "
            "this factor"
        ),
        default=1,
        required=False,
    )
    neighbors = Int(
        description=('number of x and y neighbor idxs to use for interpolation, '
                     'must even and greater > 4'
        ),
        required=False,
        default=12,
        validate=mm.validate.Range(min=4)
    )

    swc_path = InputFile(
        description='path to swc file for soma location',
        required=True
    )

class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    upright_angle = Float(
        description=(
            "Angle of rotation about the soma required to upright the input "
            "morphology. In radians counterclockwise from horizontal axis"
        ),
        required=True
    )
    upright_transform_dict = Nested(AffineDictSchema,
                                    required=False,
                                    description='Dictionary defining an affine transform')
    