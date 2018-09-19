from argschema import ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import OutputFile, Float, Dict, InputFile, Nested


class MorphologySummaryParameters(ArgSchema):

    pia_transform = Dict(description="input pia transform", required=True)
    relative_soma_depth = Float(desription="input relative soma depth", required=False)
    soma_depth = Float(description="input soma depth", required=True)
    swc_file = InputFile(description="input swc file", required=True)
    thumbnail_file = OutputFile(description="output thumbnail file", required=True)
    cortex_thumbnail_file = OutputFile(description="output cortex thumbnail file", required=True)
    normal_depth_thumbnail_file = OutputFile(description="output normal depth thumbnail file", required=True)
    high_resolution_thumbnail_file = OutputFile(description="output high resolution cortex thumbnail file", required=True)


class OutputSchema(DefaultSchema):
    input_parameters = Nested(MorphologySummaryParameters,
                              description="Input parameters the module was run with", required=True)


class OutputParameters(OutputSchema):
    pass
