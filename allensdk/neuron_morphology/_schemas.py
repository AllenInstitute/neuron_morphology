from argschema import ArgSchema
from argschema.schemas import DefaultSchema
from argschema.fields import OutputFile, Float, InputFile, Nested, List, Str, Integer, Number


class PiaTransformSchema(ArgSchema):

    id = Integer(description="", required=True)
    tvr_00 = Number(description="", required=True)
    tvr_01 = Number(description="", required=True)
    tvr_02 = Number(description="", required=True)
    tvr_03 = Number(description="", required=True)
    tvr_04 = Number(description="", required=True)
    tvr_05 = Number(description="", required=True)
    tvr_06 = Number(description="", required=True)
    tvr_07 = Number(description="", required=True)
    tvr_08 = Number(description="", required=True)
    tvr_09 = Number(description="", required=True)
    tvr_10 = Number(description="", required=True)
    tvr_11 = Number(description="", required=True)
    trv_00 = Number(description="", required=True)
    trv_01 = Number(description="", required=True)
    trv_02 = Number(description="", required=True)
    trv_03 = Number(description="", required=True)
    trv_04 = Number(description="", required=True)
    trv_05 = Number(description="", required=True)
    trv_06 = Number(description="", required=True)
    trv_07 = Number(description="", required=True)
    trv_08 = Number(description="", required=True)
    trv_09 = Number(description="", required=True)
    trv_10 = Number(description="", required=True)
    trv_11 = Number(description="", required=True)
    metric = Number(description="", required=True, allow_none=True)
    scale_x = Number(description="", required=True)
    scale_y = Number(description="", required=True)
    scale_z = Number(description="", required=True)
    rotation_x = Number(description="", required=True)
    rotation_y = Number(description="", required=True)
    rotation_z = Number(description="", required=True)
    skew_x = Number(description="", required=True)
    skew_y = Number(description="", required=True)
    skew_z = Number(description="", required=True)
    created_at = Str(description="", required=True)
    updated_at = Str(description="", required=True)


class MorphologySummaryParameters(ArgSchema):

    pia_transform = Nested(PiaTransformSchema, description="input pia transform", required=True)
    relative_soma_depth = Float(desription="input relative soma depth", required=False)
    soma_depth = Float(description="input soma depth", required=True)
    swc_file = InputFile(description="input swc file", required=True)
    thumbnail_file = OutputFile(description="output thumbnail file", required=True)
    cortex_thumbnail_file = OutputFile(description="output cortex thumbnail file", required=True)
    high_resolution_thumbnail_file = OutputFile(description="output high resolution cortex thumbnail file",
                                                required=True)
    normalized_depth_thumbnail_file = OutputFile(description="output high resolution cortex thumbnail file with "
                                                             "normalized depth", required=True)


class ReconstructionTileViewerNestedParameters(ArgSchema):

    attribute = Str(description="attribute to sort by", required=True)
    sort = Str(description="sort order of the attribute (asc or desc)", required=True)


class ReconstructionTileViewerParameters(ArgSchema):

    morphology_csv_input_file = InputFile(description="input morphology csv file", required=True)
    html_output_file = OutputFile(description="output HTML file", required=True)
    reconstruction_hierarchy = List(Nested(ReconstructionTileViewerNestedParameters), cli_as_single_argument=True,
                                    description="reconstruction hierarchy with order direction", required=True)
    reconstruction_card_properties = List(Nested(ReconstructionTileViewerNestedParameters), cli_as_single_argument=True,
                                          description="reconstruction card properties with order direction",
                                          required=True)
    max_columns = Str(description="number of columns in the viewer (it could be None)", required=False)


class MorphologyFeatureParameters(ArgSchema):

    pia_transform = PiaTransformSchema
    swc_file = InputFile(description="input swc file", required=True)
    relative_soma_depth = Float(description="relative soma depth", required=True)


class OutputSchema(DefaultSchema):
    input_parameters = Nested(MorphologySummaryParameters,
                              description="Input parameters the module was run with", required=True)


class OutputParameters(OutputSchema):
    pass
