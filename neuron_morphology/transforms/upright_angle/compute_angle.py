from typing import Dict, Optional, List, Any

import logging
import copy as cp

import numpy as np
from scipy.interpolate import interp2d
import xarray as xr

from argschema.argschema_parser import ArgSchemaParser
from neuron_morphology.transforms.upright_angle._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.morphology import Morphology
from neuron_morphology.swc_io import morphology_from_swc
import neuron_morphology.transforms.affine_transform as aff


def get_upright_angle(gradient: xr.DataArray,
                      point: Optional[List[float]] = None,
                      n_win: int = 2) -> float:

    """
        Calculate the upright angle at a position, e.g. soma, given a vector field

        Parameters
        ----------
        gradient: xarray of the the vector field
        point: list [x,y,z] coordinates
        n_win: number of grid points to define the interpolation window

        Returns
        -------
        angle

    """

    if not point:
        point = [0, 0, 0]

    x_point, y_point, z_point = point

    nx_idx = np.searchsorted(gradient.x, x_point)
    ny_idx = np.searchsorted(gradient.y, y_point)

    # Only use the  n_win points on each side, because if
    # the full array has any nans, interp2d will return nan

    x_win = gradient.x[nx_idx - n_win:nx_idx + n_win]
    y_win = gradient.y[ny_idx - n_win:ny_idx + n_win]

    values_win = gradient[
             nx_idx - n_win:nx_idx + n_win,
             ny_idx - n_win:ny_idx + n_win,
             :]

    # Also transpose because if x=m,y=n, interp2d requires z=(n,m)
    f_dx = interp2d(x_win, y_win, values_win[:, :, 0].T)
    f_dy = interp2d(x_win, y_win, values_win[:, :, 1].T)

    dx = f_dx(x_point, y_point)
    dy = f_dy(x_point, y_point)

    return np.pi / 2 - np.arctan2(dy[0], dx[0])

def calculate_transform(gradient_field: xr.DataArray,
         morph: Morphology,
         node: Optional[List[float]] = None,
                      ):
    theta = get_upright_angle(gradient_field, node)
    transform = np.eye(4)
    transform[0:3, 0:3] = aff.rotation_from_angle(theta)

    soma = morph.get_soma()

    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    transform[0:3,3] = np.asarray([
        -soma["x"] * cos_theta + soma["y"] * sin_theta + soma["x"],
        -soma["x"] * sin_theta - soma["y"] * cos_theta + soma["y"],
        0
    ])

    output = {
        'upright_transform': aff.AffineTransform(transform),
        'upright_angle': theta
    }

    return output

def run_upright_angle(gradient_path: str,
         swc_path: str,
         node: Optional[List[float]] = None,
                      ):

    try:
        gradient_field = xr.open_dataarray(gradient_path)
    except IOError:
        raise IOError(f"Cannot find file with the gradient field in {gradient_path}")

    morph = morphology_from_swc(swc_path)

    output = calculate_transform(gradient_field, morph, node)
    output["upright_transform_dict"] = output.pop("upright_transform").to_dict()

    return output


def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = run_upright_angle(
        args["gradient_path"],
        args["swc_path"],
        args["node"],
    )
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__":
    main()
