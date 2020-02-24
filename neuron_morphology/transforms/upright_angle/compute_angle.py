from typing import Dict, Optional, List, Any

import logging
import copy as cp

import numpy as np
from scipy.interpolate import interp2d
import xarray as xr

from argschema.argschema_parser import ArgSchemaParser
from neuron_morphology.transforms.upright_angle._schemas import (
    InputParameters, OutputParameters)
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

    upright_angle = np.pi / 2 - np.arctan2(dy[0], dx[0])

    return upright_angle

        return interpolate_angle_from_gradient(gradient_ds, node)


def run_upright_angle(gradient_path: str,
         swc_path: str,
         node:Optional[List[float]],
         step: int = 10, 
         neighbors: int = 8):
    
    theta = get_upright_angle(gradient_path, node, step, neighbors)
    transform = np.eye(4)
    transform[0:3, 0:3] = aff.rotation_from_angle(theta)

    morph = morphology_from_swc(swc_path)
    soma = morph.get_soma()
    
    cos_theta = np.cos(theta)
    sin_theta = np.sin(theta)

    transform[0:3,3] = np.asarray([
        -soma["x"] * cos_theta + soma["y"] * sin_theta + soma["x"],
        -soma["x"] * sin_theta - soma["y"] * cos_theta + soma["y"],
        0
    ])
    
    output = {
        'upright_transform_dict': aff.AffineTransform(transform).to_dict(),
        'upright_angle': str(theta)
    }
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
        args["step"],
        args["neighbors"]
    )
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__":
    main()
