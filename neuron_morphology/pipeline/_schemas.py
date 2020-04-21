from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, OutputFile, String, Nested, Dict, List, Int, Field, Float)
from marshmallow import ValidationError


class PathResolution(DefaultSchema):
    path = String(
        description="the drawing line path points", 
        required=True
    )

    resolution = Float(
        description="resolution",
        required=True
    )


class PrimaryBoundaries(DefaultSchema):
    Soma = Nested(
        PathResolution,
        description="soma drawing", 
        required=True
    )

    White_Matter = Nested(
        PathResolution,
        description="white matter drawing",
        required=False
    )

    Pia = Nested(
        PathResolution,
        description=("pia drawing"),
        required=False
    )


class InputParameters(ArgSchema):
    s3_bucket_name = String(
        description="s3 landing bucket",
        required=True
    )

    neuron_reconstruction_id = Int(
        description="neuron reconstruction id",
        required=True,
        allow_none=True
    )

    specimen_id = Int(
        description="specimen id",
        required=True
    )

    primary_boundaries = Nested(
        PrimaryBoundaries,
        description="primary boundaries",
        required=True
    )
    
    swc_file = String(
        description="path to input swc (csv) file", 
        required=True
    )

    cell_depth = Float(
        description="cell depth",
        required=True,
        allow_none=True
    )

    cut_thickness = Float(
        description="cut thickness",
        required=True,
        allow_none=True
    )

    marker_file = String(
        description="path to input marker (csv) file", 
        required=True
    )

    ccf_soma_xyz = List(
        String,
        cli_as_single_argument=True,
        description="soma position in CCF", 
        required=True
    )
