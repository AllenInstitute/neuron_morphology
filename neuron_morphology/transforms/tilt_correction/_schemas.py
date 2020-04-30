import marshmallow as mm
from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, List, Float, Int, Nested
)
from neuron_morphology.transforms.affine_transformer._schemas import (
    AffineDictSchema, AffineListSchema
)


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description='path to swc file for soma location',
        required=True
    )
    marker_path = InputFile(
        description='path to marker file',
        required=True
    )
    ccf_path = InputFile(
        description='path to common cortical framework streamline file',
        required=True
    )
    slice_transform_list = Nested(
        AffineListSchema,
        description='List defining the transform defining the slice cut angle',
        required=False
    )


class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters,
        description="The parameters argued to this executable",
        required=True
    )
    tilt_angle = Float(
        description='Tilt correction about x axis to align with streamlines',
        required=True
    )
    tilt_transform_dict = Nested(AffineDictSchema,
                                 required=False,
                                 description='Dictionary defining an affine transform')
