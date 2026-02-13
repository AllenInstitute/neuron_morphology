from argschema.schemas import ArgSchema, DefaultSchema
from argschema.fields import (
    InputFile, OutputFile, String, Nested, Dict, List, Int, Field, Float, Boolean)
from marshmallow import ValidationError


class PathResolution(DefaultSchema):
    path = String(
        description="Fixed value boundary condition",
        required=True
    )

    resolution = Float(
        description="Resolution of pixels in microns",
        required=True
    )


class PrimaryBoundaries(DefaultSchema):
    Soma = Nested(
        PathResolution,
        description='string alternating x, y coordinates outlining the soma. '
                    'If provided, streamlines will be translated so that '
                    'the origin is at the soma',
        required=True
    )

    White_Matter = Nested(
        PathResolution,
        description="Fixed value white matter boundary condition",
        required=False
    )

    Pia = Nested(
        PathResolution,
        description=("Fixed value pia boundary condition"),
        required=False
    )

class S3LandingBucket(DefaultSchema):
    name = String(
        description="s3 landing bucket name or access point arn",
        required=True
    )

    region = String(
        description="s3 landing bucket's region",
        required=True
    )

    credentials_file = String(
        description="the INI config file path to the s3 landing bucket's credentials",
        required=False
    )

class InputParameters(ArgSchema):

    destination_bucket = Nested(
        S3LandingBucket,
        description="s3 landing bucket info (bucket_name/access_point_arn and region)",
        required=True
    )

    neuron_reconstruction_id = Int(
        description="neuron reconstruction id",
        required=True,
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
        Float,
        cli_as_single_argument=True,
        description="soma location (x,y,z) coordinates in CCF",
        required=True
    )

    slice_transform = List(
        Float,
        cli_as_single_argument=True,
        description='List defining the transform defining slice cut angle',
        required=True,
        allow_none=True,
    )

    slice_image_flip = Boolean(
        description=('indicates whether the image was flipped relative '
                     'to the slice (avg_group_label.name = \'Flip Slice Indicator\''),
        required=True
    )
