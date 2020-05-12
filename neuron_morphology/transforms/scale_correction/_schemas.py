import marshmallow as mm
from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, List, Float, Int, Nested
)
from neuron_morphology.transforms.affine_transformer._schemas import (
    AffineDictSchema
)


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description='path to swc file',
        required=True
    )
    marker_path = InputFile(
        description='path to marker file',
        required=True
    )
    soma_depth = Float(
        description='Recorded Depth of soma in slice',
        required=True,
    )
    cut_thickness = Float(
        description='Thickness of the slice when cut',
        required=False,
        default=350.,
    )


class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters,
        description="The parameters argued to this executable",
        required=True
    )
    scale_correction = Float(
        description=(
            "Z axis scale factor to correct for slice shrinkage"
        ),
        required=True
    )
    scale_transform = Nested(AffineDictSchema,
                                  required=False,
                                  description='Dictionary defining an affine transform')
