import argschema as ags
from neuron_morphology._schemas import ReconstructionTileViewerParameters
import neuron_morphology.rendering.reconstruction_tile_viewer as mv


def main():

    module = ags.ArgSchemaParser(schema_type=ReconstructionTileViewerParameters)
    mv.create_tile_viewer(module.args["morphology_csv_file"],
                          module.args["html_file"],
                          module.args["reconstruction_hierarchy"],
                          module.args["reconstruction_card_properties"],
                          module.args["max_columns"])


if __name__ == "__main__":
    main()
