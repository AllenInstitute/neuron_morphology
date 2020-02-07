import logging
import copy as cp
from typing import Dict

import numpy as np
from scipy import ndimage as ndi
import rasterio.features
import shapely

from argschema.argschema_parser import ArgSchemaParser

from neuron_morphology.snap_polygons._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.snap_polygons._from_lims import FromLimsSource
from neuron_morphology.snap_polygons.bounding_box import BoundingBox
from neuron_morphology.snap_polygons.geometries import Geometries

def make_scale_transform(scale: float):
    return lambda vertical, horizontal: (vertical * scale, horizontal * scale)

def clear_overlaps(stack: Dict[str, np.ndarray]):
    overlaps = np.array(list(stack.values())).sum(axis=0) >= 2

    for image in stack.values():
        image[overlaps] = 0

def closest_from_stack(stack: Dict[str, np.ndarray]):

    distances = []
    names = {}

    for ii, (name, mask) in enumerate(stack.items()):
        distances.append(ndi.distance_transform_edt(1 - mask))
        names[ii + 1] = name

    closest = np.squeeze(np.argmin(distances, axis=0)) + 1
    return closest, names

def get_snapped_polys(closest, name_lut):
    return {
        name_lut[int(label)]: 
            shapely.geometry.polygon.Polygon(poly["coordinates"][0])
        for poly, label
        in rasterio.features.shapes(closest.astype(np.uint16))
    }

def main(
    layer_polygons, 
    pia_surface, 
    wm_surface, 
    image_dimensions,
    working_scale: float,
    images=None
):
    """
    """

    original_box = BoundingBox(
        0.0, 0.0, image_dimensions["height"], image_dimensions["width"])
    geometries = Geometries(original_box)
    geometries.register_polygons(layer_polygons)
    geometries.register_surface("pia", pia_surface["path"])
    geometries.register_surface("wm", wm_surface["path"])

    scale_transform = make_scale_transform(working_scale)
    working_geo = geometries.transform(scale_transform)

    raster_stack = working_geo.rasterize()
    clear_overlaps(raster_stack)
    closest, closest_names = closest_from_stack(raster_stack)
    snapped_polys = get_snapped_polys(closest, closest_names)

    result_geos = Geometries(working_geo.close_bounds)
    result_geos.register_polygons(snapped_polys)

    stack = result_geos.rasterize()

    import matplotlib.pyplot as plt
    for _, img in stack.items():
        fig, ax = plt.subplots()
        ax.imshow(img)
    
    fig, ax = plt.subplots()
    ax.imshow(closest)

    plt.show()

if __name__ == "__main__":

    class Parser(ArgSchemaParser):
        """
        """
        default_configurable_sources = \
            ArgSchemaParser.default_configurable_sources + [FromLimsSource]

    parser = Parser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    main(**args)