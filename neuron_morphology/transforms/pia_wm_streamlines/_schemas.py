from argschema import ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import (
    Nested, String, Int, Float, OutputDir, OutputFile, NumpyArray)


class PiaWmStreamlineSchema(ArgSchema):
    """Arg Schema for run_pia_wm_streamlines"""

    pia_path_str = String(
        required=True,
        description='string alternating x, y coordinates outlining the pia')
    wm_path_str = String(
        required=True,
        description='string alternating x, y coordinates outlining the wm')
    soma_path_str = String(
        required=False,
        description='string alternating x, y coordinates outlining the soma. '
                    'If provided, streamlines will be translated so that '
                    'the origin is at the soma')
    resolution = Float(required=False,
                       default=1,
                       description='Resolution of pixels in microns')
    pia_fixed_value = Float(required=False,
                            default=1,
                            description='Fixed value pia boundary condition')
    wm_fixed_value = Float(required=False,
                           default=0,
                           description='Fixed value wm boundary condition')
    mesh_res = Int(required=False,
                   default=20,
                   description='Resolution for mesh for laplace solver')
    output_dir = OutputDir(required=True,
                           description='Directory to write xarray results')


class OutputParameters(DefaultSchema):
    inputs = Nested(
        PiaWmStreamlineSchema,
        description="The parameters argued to this executable",
        required=True
    )
    depth_field_file = OutputFile(
        required=True,
        description='location of depth field xarray')

    gradient_field_file = OutputFile(
        required=True,
        description='location of gradient field xarray')
    translation = NumpyArray(
        required=False,
        description='translation if applied')
