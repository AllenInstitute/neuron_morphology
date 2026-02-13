from typing import Dict, List, Tuple, Optional
import copy as cp
import logging

import numpy as np
import pandas as pd
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
from shapely.geometry.polygon import Polygon
from shapely.geometry import LineString, Point

from argschema.argschema_parser import ArgSchemaParser

from neuron_morphology.swc_io import morphology_from_swc
from neuron_morphology.layered_point_depths._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.features.layer.layered_point_depths import (
    LayeredPointDepths)

def translate_field(
    field: xr.DataArray,
    by_x: float,
    by_y: float,
    inplace: bool = False
):
    """ Translate a spatial xarray dataset

    Parameters
    ----------
    field : to be translated
    by_x : =the translation along x
    by_y : the translation along y
    inplace : If True, modify this dataarray, otherwise modify a copy

    Returns
    -------
    translated dataarray, potentiall the same as the input

    """

    if not inplace:
        field = field.copy()

    field = field.assign_coords(x=(field.x + by_x))
    field = field.assign_coords(y=(field.y + by_y))

    return field

def setup_interpolator(
    field: xr.DataArray,
    dim: Optional[str],
    **kwargs
) -> RegularGridInterpolator:
    """ Build a regular grid interpolator from a dataarray

    Parameters
    ----------
    field : Must have dimensions "x" and "y". May have dimension "dim"
    dim : base the interpolator on values from this dim slice. If None, ignore
        dim
    **kwargs : passed to interpolator constructor

    Returns
    -------
    a callable interpolator

    """

    coords = (field["x"].values, field["y"].values)
    if field.dims.index("x") == 1:
        coords = coords[::-1]

    if dim is None:
        values = field.values
    else:
        values = field.loc[{"dim": dim}].values

    return RegularGridInterpolator(coords, values, **kwargs)

def containing_layer(
    pos: Tuple[float, float],
    layers: List[Dict]
) -> Optional[str]:
    """ Find the layer in which a point is contained

    Parameters
    ----------
    pos : the coordinate of the point
    layers : Each has "name" - a string and "bounds" - a Polygon

    Returns
    -------
    The name of the containing layer or None if no containing layer was found

    """

    in_layer = [
        layer["name"] for layer in layers if
        layer["bounds"].intersects(Point(*pos)) # checks for common boundary or interior
    ]

    if len(in_layer) == 0:
        return None
    elif len(in_layer) == 1:
        return in_layer[0]
    else:
        raise ValueError(f"overlapping layers: {in_layer}")


def tuplize(arr: np.array) -> Tuple:
    """ Convert an array to a tuple
    """
    return tuple(arr.tolist())


def step_from_node(
    pos: Tuple[float, float],
    depth_interp: RegularGridInterpolator,
    dx_interp: RegularGridInterpolator,
    dy_interp: RegularGridInterpolator,
    surface: LineString,
    step_size: float,
    max_iter: int,
    adaptive_scale: int = 32,
) -> Optional[float]:
    """ Walk through a gradient field, until a defined surface is passed.

    Parameters
    ----------
    pos : the start position
    depth_interp : callable mapping positions to scalar depth values
    dx_interp : callable mapping positions to the x component of the gradient
    dy_interp : callable mapping positions to the y component of the gradient
    surface : Check for the intersection of the path with this surface
    step_size : Each step proceeds in the direction of the local gradient,
        scaled to this step size
    max_iter : give up (return None) if the surface is not intersected in this
        many steps

    Returns
    -------
    The depth of the intersection between the path walked and the given surface

    """

    retry_step = False
    cur_pos = np.array(list(pos))

    for _ in range(max_iter):
        if not retry_step:
            # skip recalculating base_step when retrying with smaller step
            dx = dx_interp(cur_pos)
            dy = dy_interp(cur_pos)

            base_step = np.squeeze([dx, dy])
            if np.any(np.isnan(base_step)):
                return None
            base_step = base_step / np.linalg.norm(base_step)
        step = adaptive_scale * step_size * base_step

        next_pos = cur_pos + step
        ray = LineString([tuplize(cur_pos), tuplize(next_pos)])

        intersection = ray.intersection(surface)
        if not intersection.is_empty:
            if adaptive_scale > 1:
                # We intersected, but with a big step; scale it down and try again
                # from same starting point
                adaptive_scale /= 2
                retry_step = True
                continue
            else:
                if intersection.geom_type == "MultiPoint":
                    cur_pt = Point(cur_pos)
                    dist = np.inf
                    for test_pt in intersection:
                        test_dist = cur_pt.distance(test_pt)
                        if test_dist < dist:
                            dist = test_dist
                            closest_pt = test_pt
                    intersection_pt = list(closest_pt.coords)
                else:
                    intersection_pt = list(intersection.coords)
                return float(depth_interp(intersection_pt[0]))

        cur_pos = next_pos
        retry_step = False

    return None # uneccessary, but satisfies linter :/


def get_node_intersections(
    node: Dict,
    depth_interp: RegularGridInterpolator,
    dx_interp: RegularGridInterpolator,
    dy_interp: RegularGridInterpolator,
    layers: List[Dict],
    step_size: float,
    max_iter: int
) -> Dict:
    """ Given a node, find its layer and intersection depths. Then return a row
    of LayeredPointDepths for this node.

    Parameters
    ----------
    node : Of a Morphology. must have:
        "id" - unique identifier
        "type" - which kind of node is this?
        "x", "y" - positions in x and y of this node
    depth_interp : callable mapping positions to scalar depth values
    dx_interp : callable mapping positions to the x component of the gradient
    dy_interp : callable mapping positions to the y component of the gradient
    layers : Each has
        "name" - an identifier
        "bounds" - a Polygon describing the entire boundary
        "pia_surface" - a LineString describing the piaward surface of this
            layer
        "wm_surface" - a LineString describing the white matter-wise surface of
            this layer
    step_size : Each step proceeds in the direction of the local gradient,
        scaled to this step size
    max_iter : give up (return None) if the surface is not intersected in this
        many steps

    Returns
    -------
    A dictionary representing a single row of LayeredPointDepths. Has Keys:
        "ids" - the identifier of this node
        "layer_name" - the layer containing this node
        "depth" - the depth of this node
        "local_layer_pia_side_depth" - the depth of the intersection between
            this node's steepest ascent path and the piaward surface of its
            containing layer
        "local_layer_wm_side_depth" - the depth of the intersection between
            this node's steepest ascent path and the white matterward surface
            of its containing layer
        "point_type": The type of this node

    """

    pos = (node["x"], node["y"])
    start_layer = containing_layer(pos, layers)
    depth = float(depth_interp(pos))

    if start_layer is None:
        return {
            "ids": node["id"],
            "layer_name": start_layer,
            "depth": depth,
            "local_layer_pia_side_depth": None,
            "local_layer_wm_side_depth": None,
            "point_type": node["type"]
        }

    pia = [
        layer["pia_surface"] for layer in layers
        if layer["name"] == start_layer
    ][0]
    wm = [
        layer["wm_surface"] for layer in layers
        if layer["name"] == start_layer
    ][0]

    return {
        "ids": node["id"],
        "layer_name": start_layer,
        "depth": depth,
        "local_layer_pia_side_depth": step_from_node(
            pos, depth_interp, dx_interp, dy_interp, pia, step_size, max_iter
        ),
        "local_layer_wm_side_depth": step_from_node(
            pos, depth_interp, dx_interp, dy_interp, wm, -step_size, max_iter
        ),
        "point_type": node["type"]
    }

def setup_layers(layers: List[Dict]):
    """ Convert layer bounds, pia, and white matter surfaces to shapely objects

    Parameters
    ----------
    layers : Mutated inplace. Has keys:
        "bounds" - a Polygon describing the entire boundary
        "pia_surface" - a LineString describing the piaward surface of this
            layer
        "wm_surface" - a LineString describing the white matter-wise surface of
            this layer
    """

    for layer in layers:
        layer["bounds"] = Polygon(layer["bounds"])
        layer["pia_surface"] = LineString(layer["pia_surface"])
        layer["wm_surface"] = LineString(layer["wm_surface"])

def run_layered_point_depths(
    swc_path: str,
    depth: Dict,
    layers: List[Dict],
    step_size: float,
    max_iter: int,
    output_path: str
):

    morpho = morphology_from_swc(swc_path)
    gradient_field: xr.DataArray = xr.open_dataarray(depth["gradient_field_path"])
    depth_field: xr.DataArray = xr.open_dataarray(depth["depth_field_path"])
    setup_layers(layers)
    step_size = depth["pia_sign"] * step_size

    if depth["soma_origin"]:
        soma = morpho.get_soma()
        translate_field(
            gradient_field,
            soma["x"],
            soma["y"],
            inplace=True
        )
        translate_field(
            depth_field,
            soma["x"],
            soma["y"],
            inplace=True
        )

    depth_interp = setup_interpolator(
        depth_field, None, method="linear",
        bounds_error=False, fill_value=None)
    dx_interp = setup_interpolator(
        gradient_field, "dx", method="linear",
        bounds_error=False, fill_value=None)
    dy_interp = setup_interpolator(
        gradient_field, "dy", method="linear",
        bounds_error=False, fill_value=None)

    outputs = []
    for node in morpho.nodes():
        outputs.append(get_node_intersections(
            node,
            depth_interp,
            dx_interp,
            dy_interp,
            layers,
            step_size,
            max_iter
        ))

    depths = LayeredPointDepths.from_dataframe(pd.DataFrame(outputs))
    depths.to_csv(output_path)

    gradient_field.close()
    depth_field.close()

    return {"output_path": output_path}


def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = main(**args)
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__": main()
