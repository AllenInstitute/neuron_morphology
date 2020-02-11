import marshmallow as mm

from argschema import ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import (
    Nested, Float, List, InputFile, OutputFile)


def validate_input_affine(data):
    has_affine_dict = bool(data.get('affine_dict'))
    has_affine_list = bool(data.get('affine_list'))
    if has_affine_list and has_affine_dict:
        err_msg = 'Provide either affine_list or affine_dict, not both'
        raise mm.ValidationError(err_msg)
    elif not has_affine_list and not has_affine_dict:
        err_msg = 'Provide either affine_list or affine_dict'
        raise mm.ValidationError(err_msg)


class AffineDictSchema(DefaultSchema):
    """
    affine_dict: keys and values corresponding to the following
                [[tvr_00 tvr_01 tvr_02 tvr_09]
                 [tvr_03 tvr_04 tvr_05 tvr_10]
                 [tvr_06 tvr_07 tvr_08 tvr_11]
                 [0      0      0      1]]
    """
    tvr_00 = Float(required=True)
    tvr_01 = Float(required=True)
    tvr_02 = Float(required=True)
    tvr_03 = Float(required=True)
    tvr_04 = Float(required=True)
    tvr_05 = Float(required=True)
    tvr_06 = Float(required=True)
    tvr_07 = Float(required=True)
    tvr_08 = Float(required=True)
    tvr_09 = Float(required=True)
    tvr_10 = Float(required=True)
    tvr_11 = Float(required=True)


class ApplyAffineSchema(ArgSchema):
    """Arg Schema for apply_affine_transform module"""
    affine_dict = Nested(AffineDictSchema,
                         required=False,
                         description='Dictionary defining an affine transform')
    affine_list = List(Float,
                       required=False,
                       cli_as_single_argument=True,
                       description='List defining an affine transform')
    input_swc = InputFile(required=True,
                          description='swc file to be transformed')

    output_swc = OutputFile(required=True,
                            description='Output swc filepath')

    @mm.validates_schema
    def validate_schema_input(self, data):
        validate_input_affine(data)


class OutputParameters(DefaultSchema):
    inputs = Nested(
        ApplyAffineSchema,
        description="The parameters argued to this executable",
        required=True
    )
    transformed_swc = OutputFile(
        required=True,
        description='location of the transformed swc')
