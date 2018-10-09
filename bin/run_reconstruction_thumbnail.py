#!/usr/bin/python

import argschema as ags
from allensdk.neuron_morphology._schemas import MorphologySummaryParameters
import allensdk.core.json_utilities as ju
import allensdk.neuron_morphology.rendering.reconstruction_thumbnail as rt


def run_reconstruction_thumbnail(pia_transform, relative_soma_depth, soma_depth, swc_file, thumbnail_file,
                                 cortex_thumbnail_file, high_resolution_thumbnail_file,
                                 normalized_depth_thumbnail_file):

    cortex_thumbnail_width = 100
    cortex_thumbnail_height = 100
    thumbnail_width = 100
    thumbnail_height = 100
    high_resolution_thumbnail_width = 400
    high_resolution_thumbnail_height = 400

    morphology_summary_img = rt.morphology_summary_thumbnail(swc_file, cortex_thumbnail_width, cortex_thumbnail_height,
                                                             [1, 2, 3, 4], pia_transform)

    morphology_summary_img.save(cortex_thumbnail_file)

    morphology_summary_density_graph_img = rt.morphology_summary_density_graph_thumbnail(swc_file, soma_depth,
                                                                                         relative_soma_depth,
                                                                                         thumbnail_width,
                                                                                         thumbnail_height,
                                                                                         [1, 2, 3, 4],
                                                                                         pia_transform, scale_bar=True)
    morphology_summary_density_graph_img.save(thumbnail_file)

    morphology_summary_density_graph_high_res_img = rt.morphology_summary_density_graph_thumbnail(swc_file, soma_depth,
                                                                                                  relative_soma_depth,
                                                                                                  high_resolution_thumbnail_width,
                                                                                                  high_resolution_thumbnail_height,
                                                                                                  [1, 2, 3, 4],
                                                                                                  pia_transform,
                                                                                                  scale_bar=True)
    morphology_summary_density_graph_high_res_img.save(high_resolution_thumbnail_file)

    morphology_summary_density_graph_img = rt.morphology_summary_density_graph_thumbnail(swc_file, soma_depth,
                                                                                         relative_soma_depth,
                                                                                         high_resolution_thumbnail_width,
                                                                                         high_resolution_thumbnail_height,
                                                                                         [1, 2, 3, 4], pia_transform,
                                                                                         normalized_depth=True)

    morphology_summary_density_graph_img.save(normalized_depth_thumbnail_file)


def main():

    module = ags.ArgSchemaParser(schema_type=MorphologySummaryParameters)
    run_reconstruction_thumbnail(module.args["pia_transform"],
                                 module.args["relative_soma_depth"],
                                 module.args["soma_depth"],
                                 module.args["swc_file"],
                                 module.args["thumbnail_file"],
                                 module.args["cortex_thumbnail_file"],
                                 module.args["high_resolution_thumbnail_file"],
                                 module.args["normalized_depth_thumbnail_file"])

    ju.write(module.args["output_json"], {})


if __name__ == "__main__":
    main()
