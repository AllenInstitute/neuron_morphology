from PIL import Image
import neuron_morphology.rendering.density_graph as dg
import neuron_morphology.rendering.morphology_summary as ms
import neuron_morphology.swc_io as swc
import neuron_morphology.rendering.colors as co
from PIL import ImageDraw


def _draw_scale_bar(img, morphology_top, morphology_bottom, density_graph_top, density_graph_bottom, density_graph_left,
                    reference_line, color):

    canvas = ImageDraw.Draw(img)
    canvas.line((density_graph_left, density_graph_top, reference_line, morphology_top), color)
    canvas.line((density_graph_left, density_graph_bottom, reference_line, morphology_bottom), color)
    canvas.line((reference_line, morphology_top, reference_line, morphology_bottom), color)


def density_graph_thumbnail(swc_file, soma_depth, relative_soma_depth, thumbnail_width, thumbnail_height,
                            ordered_node_types, padding_left=0, padding_right=0, padding_top=0, padding_bottom=0):

    drawing_area_width = thumbnail_width - (padding_left + padding_right)
    drawing_area_height = thumbnail_height - (padding_top + padding_bottom)
    offset = (padding_right, padding_top)

    morphology = swc.morphology_from_swc(swc_file)
    density_graph = dg.DensityGraph(morphology, drawing_area_width, drawing_area_height,
                                    soma_depth, relative_soma_depth, ordered_node_types)
    density_draph_img = density_graph.draw_histograms()
    img = Image.new('RGBA', (thumbnail_width, thumbnail_height))
    img.paste(density_draph_img, offset)
    return img


def morphology_summary_thumbnail(swc_file, thumbnail_width, thumbnail_height,
                                 ordered_node_types, pia_transform, padding_left=5, padding_right=5, padding_top=5,
                                 padding_bottom=5):

    drawing_area_width = thumbnail_width - (padding_left + padding_right)
    drawing_area_height = thumbnail_height - (padding_top + padding_bottom)
    offset = (padding_left, padding_top)

    morphology = swc.morphology_from_swc(swc_file)
    morphology_summary = ms.MorphologySummary(morphology, pia_transform, drawing_area_width, drawing_area_height,
                                              ordered_node_types)

    morphology_summary_img = morphology_summary.draw_morphology_summary()
    img = Image.new('RGBA', (thumbnail_width, thumbnail_height))
    img.paste(morphology_summary_img, offset)
    return img


def morphology_summary_density_graph_thumbnail(swc_file, soma_depth, relative_soma_depth, thumbnail_width,
                                               thumbnail_height, ordered_node_types, pia_transform, padding_left=5,
                                               padding_right=5, padding_top=5, padding_bottom=5,
                                               normalized_depth=False, scale_bar=False,
                                               scale_bar_color=co.Colors().scale_bar_color):

    drawing_area_width = thumbnail_width - (padding_left + padding_right)
    drawing_area_height = thumbnail_height - (padding_top + padding_bottom)
    morphology_summary_drawing_area_width = (drawing_area_width * 4 // 5) - padding_right
    density_graph_drawing_area_width = (drawing_area_width // 5) - padding_left

    morphology = swc.morphology_from_swc(swc_file)

    density_graph = dg.DensityGraph(morphology, density_graph_drawing_area_width, drawing_area_height,
                                    soma_depth, relative_soma_depth, ordered_node_types)

    density_graph_img = density_graph.draw_histograms()

    morphology_summary_offset = (padding_left, padding_top)
    density_graph_offset = (padding_left + morphology_summary_drawing_area_width + padding_left * 2, padding_top)

    if normalized_depth:
        drawing_area_height = density_graph.bottom() - density_graph.top()
        morphology_summary_offset = (padding_left, density_graph.top())

    morphology_summary = ms.MorphologySummary(morphology, pia_transform, morphology_summary_drawing_area_width,
                                              drawing_area_height, ordered_node_types)
    morphology_summary_img = morphology_summary.draw_morphology_summary()

    img = Image.new('RGBA', (thumbnail_width, thumbnail_height))
    img.paste(morphology_summary_img, morphology_summary_offset)
    img.paste(density_graph_img, density_graph_offset)

    if scale_bar:

        morphology_top = padding_top + morphology_summary.top()
        morphology_bottom = padding_top + morphology_summary.bottom()

        if normalized_depth:
            morphology_top = padding_top + density_graph.top()
            morphology_bottom = padding_top + drawing_area_height + density_graph.top()

        density_graph_top = padding_top + density_graph.top()
        density_graph_bottom = padding_top + density_graph.bottom()
        density_graph_left = padding_right + morphology_summary_drawing_area_width + padding_left
        reference_line = padding_right + (morphology_summary_drawing_area_width // 2)
        _draw_scale_bar(img, morphology_top, morphology_bottom, density_graph_top, density_graph_bottom,
                        density_graph_left, reference_line, scale_bar_color)

    return img
