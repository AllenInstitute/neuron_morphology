import marshmallow as mm
from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, List, Float, Int, Nested
)
from neuron_morphology.transforms.affine_transformer._schemas import (
    AffineDictSchema
)

def validate_neighbors(num):
    if num<4 or (num % 2) != 0:
        err_msg = ("The number of neighbors for interpolation must be an even and greater than 4")
        raise mm.ValidationError(err_msg)
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
        # min data points must be >= (k+1)**2, k=1 for linear
    )

    swc_path = InputFile(
        description='path to swc file for soma location',
        required=True
    )
    
    @mm.validates_schema
    def validate_schema_input(self, data):
        validate_neighbors(data.get('neighbors'))

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
    