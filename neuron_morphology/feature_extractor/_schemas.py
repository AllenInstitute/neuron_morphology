from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import InputFile, OutputFile, String, Nested, Dict


class InputParameters(ArgSchema):
    swc_path = InputFile(
        description="path to input swc (csv) file", 
        required=True
    )
    feature_set = String(
        description="select the basic set of features to calculate",
        required=False,
        default="aibs_default"
    )
    only_marks = String(
        description=(
            "restrict calculated features to those with this set of marks"
        ), 
        required=False,
        many=True
    )
    required_marks = String(
        description=(
            "Error (vs. skip) if any of these marks fail validation"
        ), 
        required=False,
        many=True
    )
    additional_output_path = OutputFile(
        description=(
            "this module writes outputs to a json specified as --output_json. "
            "If you want to store outputs in a different format "
            "(.csv is supported currently), specify this parameter"
        ),
        required=False
    )

class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    results = Dict(
        description="The outputs of feature extraction"
        required=True
    )