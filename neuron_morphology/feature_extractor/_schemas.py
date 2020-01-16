from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, OutputFile, String, Nested, Dict, List, Int, Field, Float)
from marshmallow import ValidationError

from neuron_morphology.features.layer.layered_point_depths import \
    LayeredPointDepths


def validate_point_depths_path(path: str):
    """ Check whether a layered point depths path is usable.
    """
    try:
        LayeredPointDepths.read(path)
    except Exception as err:
        raise ValidationError(str(err))

    return True


class ReferenceLayerDepths(DefaultSchema):
    key = String(
        description="The name of a well known set of reference layer depths", 
        required=False, 
        default=None, 
        allow_none=True
    )
    names = List(
        String, 
        description=(
            "Construct a custom sequence of layers using these names. Must "
            "also supply boundaries (there should be one more boundary than "
            "name)."
        ), 
        cli_as_single_argument=True, 
        required=False, 
        default=None, 
        allow_none=True
    )
    boundaries = List(
        Float, 
        description=(
            "Construct a custom sequence of layers using these boundaries. "
            "Must also supply names."
        ), 
        cli_as_single_argument=True, 
        required=False, 
        default=None, 
        allow_none=True
    )

    @classmethod
    def is_valid(cls, value):
        key = value.get("key", None)
        names = value.get("names", None)
        boundaries = value.get("boundaries", None)

        if key is not None:

            if names is None and boundaries is None:
                return True
            else:
                raise ValidationError(
                    "cannot supply key along with names and boundaries"
                )

        elif names is not None and boundaries is not None:

            if len(names) + 1 == len(boundaries): 
                return True
            else:
                raise ValidationError("must supply len(names) + 1 boundaries")

        else:
            raise ValidationError(
                "must supply either key or names and boundaries"
            )


class Reconstruction(DefaultSchema):
    swc_path = InputFile(
        description="path to input swc (csv) file", 
        required=True
    )
    identifier = String(
        description="unique identifier for this reconstruction",
        required=False
    )
    layered_point_depths_path = String(
        description=(
            "Path to a file containing depthwise points suitable for "
            "calculating cortical layer histograms. See "
            "neuron_morphology.features.layer.layered_point_depths for more "
            "information. This file may be a csv or tabular hdf5 file."
        ),
        required=False,
        validate=validate_point_depths_path
    )


class GlobalParameters(DefaultSchema):
    reference_layer_depths = Nested(
        ReferenceLayerDepths,
        description=(
            "Layer histograms are calculated in a reference space defined by "
            "these average layer boundary depths. You can supply your own or "
            "use a set built into neuron_morphology."
        ),
        required=False,
        validate=ReferenceLayerDepths.is_valid
    )


class InputParameters(ArgSchema):
    reconstructions = Nested(
        Reconstruction,
        description="The morphological reconstructions to be processed",
        required=True,
        many=True
    ) 
    heavy_output_path = OutputFile(
        description=(
            "features whose results are heavyweight data (e.g. the numpy "
            "arrays returned by layer histograms features) are stored here."
        ),
        required=True
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
    output_table_path = OutputFile(
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
    global_parameters = Nested(
        GlobalParameters, 
        description=(
            "provide additional configuration to this feature extraction run. "
            "This configuration will be applied to all morphologies processed."
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
        description="The outputs of feature extraction",
        required=True
    )
