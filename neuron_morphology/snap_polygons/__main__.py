"""An executable for finding close-fit boundaries between cortical layer 
polygons.
"""
import logging
import copy as cp
from functools import partial

import shapely

from argschema.argschema_parser import ArgSchemaParser

from neuron_morphology.snap_polygons._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.snap_polygons._from_lims import FromLimsSource
from neuron_morphology.snap_polygons.geometries import (
    Geometries, find_vertical_surfaces, select_largest_subpolygon
)
from neuron_morphology.snap_polygons.cortex_surfaces import trim_to_close
from neuron_morphology.snap_polygons.image_outputter import ImageOutputter
from neuron_morphology.transforms.geometry import get_vertices_from_two_lines


def run_snap_polygons(
        layer_polygons, 
        pia_surface, 
        wm_surface, 
        layer_order,
        working_scale: float,
        surface_distance_threshold: float,
        multipolygon_error_threshold: float,
        images=None
):
    """Finds and returns close fit boundaries. May write diagnostic images as 
    a side effect.
    """

    # setup input geometries
    geometries = Geometries()
    geometries.register_polygons(layer_polygons)
    
    # setup cortex boundaries
    hull = geometries.convex_hull()
    pia = trim_to_close(hull, surface_distance_threshold, pia_surface["path"])
    white_matter = trim_to_close(
        hull, surface_distance_threshold, wm_surface["path"]
    )
    
    geometries.register_surface("pia", pia)
    geometries.register_surface("wm", white_matter)

    pia_wm_vertices = get_vertices_from_two_lines(
        pia.coords[:], white_matter.coords[:]
    )
    bounds = shapely.geometry.polygon.Polygon(pia_wm_vertices)

    multipolygon_resolver = partial(
        select_largest_subpolygon, 
        error_threshold=multipolygon_error_threshold
    )

    # go!
    result_geos = (
        geometries
        .fill_gaps(working_scale, multipolygon_resolver=multipolygon_resolver)
        .cut(bounds, multipolygon_resolver=multipolygon_resolver)
    )

    # get output surfaces
    boundaries = find_vertical_surfaces(
        result_geos.polygons, 
        layer_order, 
        pia=geometries.surfaces["pia"], 
        white_matter=geometries.surfaces["wm"]
    )
    result_geos.register_surfaces(boundaries)        

    # write results
    outputter = ImageOutputter(
        geometries, result_geos, images
    )
    results = result_geos.to_json()
    results["images"] = outputter.write_images()
    return results


def main():
    """CLI entrypoint for snapping polygons
    """

    class Parser(ArgSchemaParser):
        """An ArgschemaParser that can pull data from LIMS
        """
        default_configurable_sources = \
            ArgSchemaParser.default_configurable_sources + [FromLimsSource]

    parser = Parser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = run_snap_polygons(**args)
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__":
    main()
