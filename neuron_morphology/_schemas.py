from argschema import ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import OutputFile, Float, InputFile, Nested, Int, Dict, List, Str


class MorphologySummaryParameters(ArgSchema):

    pia_transform = Dict(description="input pia transform", required=True)
    relative_soma_depth = Float(desription="input relative soma depth", required=False)
    soma_depth = Float(description="input soma depth", required=True)
    swc_file = InputFile(description="input swc file", required=True)
    thumbnail_file = OutputFile(description="output thumbnail file", required=True)
    cortex_thumbnail_file = OutputFile(description="output cortex thumbnail file", required=True)
    high_resolution_thumbnail_file = OutputFile(description="output high resolution cortex thumbnail file", required=True)


class ReconstructionTileViewerParameters(ArgSchema):

    morphology_csv_file = InputFile(description="input morphology csv file", required=True)
    html_file = OutputFile(description="output HTML file", required=True)
    reconstruction_hierarchy = List(Dict, cli_as_single_argument=True,
                                    description="reconstruction hierarchy with order direction", required=True)
    reconstruction_card_properties = List(Dict, cli_as_single_argument=True,
                                          description="reconstruction card properties with order direction",
                                          required=True)
    max_columns = Str(description="number of columns in the viewer (it could be None)", required=True)


class OutputSchema(DefaultSchema):
    input_parameters = Nested(MorphologySummaryParameters,
                              description="Input parameters the module was run with", required=True)


class OutputParameters(OutputSchema):
    pass
