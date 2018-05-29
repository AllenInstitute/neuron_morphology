#!/usr/bin/python

import argschema as ags
from neuron_morphology._schemas import ReconstructionTileViewerParameters
import neuron_morphology.rendering.reconstruction_tile_viewer as mv


def main():

    module = ags.ArgSchemaParser(schema_type=ReconstructionTileViewerParameters)
    html = mv.create_tile_viewer(module.args["morphology_csv_input_file"],
                                 module.args["reconstruction_hierarchy"],
                                 module.args["reconstruction_card_properties"],
                                 module.args["max_columns"])

    with open(module.args["html_output_file"], "w") as htmlfile:
        htmlfile.write(html)


if __name__ == "__main__":
    main()
