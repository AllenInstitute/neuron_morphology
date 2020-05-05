import marshmallow as mm
from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, List, Float, Int, Nested, Boolean
)
from neuron_morphology.transforms.affine_transformer._schemas import (
    AffineDictSchema
)


def validate_input_affine(data):
    has_slice_transform_dict = bool(data.get('slice_transform_dict'))
    has_slice_transform_list = bool(data.get('slice_transform_list'))
    if has_slice_transform_list and has_slice_transform_dict:
        err_msg = ('Provide either slice_transform_list or '
                   'slice_transform_dict, not both')
        raise mm.ValidationError(err_msg)
    elif not has_slice_transform_list and not has_slice_transform_dict:
        err_msg = 'Provide either slice_transform_list or slice_transform_dict'
        raise mm.ValidationError(err_msg)


class CSLDictSchema(DefaultSchema):
    '''Schema for CCF Soma Location'''
    x = Float(required=True)
    y = Float(required=True)
    z = Float(required=True)


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description='path to swc file for soma location',
        required=True
    )
    marker_path = InputFile(
        description='path to reconstruction marker file',
        required=True
    )
    slice_image_flip = Boolean(
        description=('indicates whether the image was flipped relative '
                     'to the slice (avg_group_label.name = \'Flip Slice Indicator\'')
    )
    ccf_soma_location = Nested(
        CSLDictSchema,
        description='Dictionary with x y z keys of CCF Soma Location (CSL)',
        required=True
    )
    slice_transform_list = List(
        Float,
        required=False,
        cli_as_single_argument=True,
        description='List defining the transform defining slice cut angle'
    )
    slice_transform_dict = Nested(
        AffineDictSchema,
        description='Dict defining the transform defining the slice cut angle',
        required=False
    )
    ccf_path = InputFile(
        description='path to common cortical framework streamline file',
        required=True
    )

    @mm.validates_schema
    def validate_schema_input(self, data):
        validate_input_affine(data)


class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters,
        description="The parameters argued to this executable",
        required=True
    )
    tilt_correction = Float(
        description='Tilt correction about x axis to align with streamlines (radians)',
        required=True
    )
    tilt_transform_dict = Nested(AffineDictSchema,
                                 required=False,
                                 description='Dictionary defining an affine transform')
