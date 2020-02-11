from typing import Dict
import collections

from scipy import ndimage
import numpy as np
import shapely
import rasterio

from neuron_morphology.snap_polygons.types import ensure_linestring


def make_scale_transform(scale: float = 1.0):
    return lambda vertical, horizontal: (vertical * scale, horizontal * scale)

def clear_overlaps(stack: Dict[str, np.ndarray]):
    overlaps = np.array(list(stack.values())).sum(axis=0) >= 2

    for image in stack.values():
        image[overlaps] = 0

def closest_from_stack(stack: Dict[str, np.ndarray]):

    distances = []
    names = {}

    for ii, (name, mask) in enumerate(stack.items()):
        distances.append(ndimage.distance_transform_edt(1 - mask))
        names[ii + 1] = name

    closest = np.squeeze(np.argmin(distances, axis=0)) + 1
    return closest, names

def get_snapped_polys(closest, name_lut):

    return {
        name_lut[int(label)]:
            shapely.geometry.polygon.Polygon(poly["coordinates"][0])
        for poly, label
        in rasterio.features.shapes(closest.astype(np.uint16))
        if int(label) in name_lut
    }


def find_vertical_surfaces(polygons, order, pia=None, wm=None):
    names = [name for name in order if name in polygons]
    results = {}

    for ii, (up_name, down_name) in enumerate(zip(names[:-1], names[1:])):

        up = polygons[up_name]
        down = polygons[down_name]

        _same, diff = shapely.ops.shared_paths(up.exterior, down.exterior)
        faces = shapely.ops.linemerge(diff)
        coordinates = list(faces.coords)
        shared_line = ensure_linestring(coordinates)

        if ii == 0 and pia is not None:
            results[f"{up_name}_pia"] = pia
        if ii == len(names) - 2 and wm is not None:
            results[f"{down_name}_wm"] = wm
        
        results[f"{up_name}_wm"] = shared_line
        results[f"{down_name}_pia"] = shared_line

    return results
