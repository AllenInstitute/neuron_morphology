from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, OutputFile, String, Nested, Dict, List, Int)


class InputParameters(ArgSchema):
    swc_paths = List(
        InputFile,
        cli_as_single_argument=True,
        description="paths to input swc (csv) files", 
        required=False,
        default=None
    )
    feature_set = String(
        description="select the basic set of features to calculate",
        required=False,
        default="aibs_default"
    )
    only_marks = List(
        String,
        cli_as_single_argument=True,
        description=(
            "restrict calculated features to those with this set of marks"
        ), 
        required=False
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
    num_processes = Int(
        description=(
            "Run a multiprocessing pool with this many processes. "
            "Default is min(number of cpus, number of swcs). "
            "Setting num_processes to 1 will avoid a pool."
        ),
        required=False,
        default=None,
        allow_none=True
    )

class OutputParameters(DefaultSchema):
    inputs = Nested(
        InputParameters, 
        description="The parameters argued to this executable",
        required=True
    )
    results = Dict(
        description="The outputs of feature extraction",
        required=True
    )