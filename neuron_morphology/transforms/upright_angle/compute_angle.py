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


def interpolate_angle_from_gradient(gradient: xr.DataArray,
                                    node: List[float]):
    """
        Calculate the upright angle at node, e.g. a soma, given a gradient field

        Parameters
        ----------
        gradient: the gradient field stored in xarray
        node: a list [x,y,z] to present the node location 

        Returns
        -------
        upright angle

    """
    
    try:
        f_dx = interp2d(gradient.x, gradient.y, gradient.values[:,:,0])
        f_dy = interp2d(gradient.x, gradient.y, gradient.values[:,:,1])

        dx = f_dx(node[0], node[1])
        dy = f_dy(node[0], node[1])

        theta = np.pi / 2 - np.arctan2(dy[0], dx[0])
    except (RuntimeError, TypeError, NameError) as e:
            print('interpolation error')
            print(e)
            theta =  np.nan

    return theta

def get_upright_angle(gradient_path: str,
                      node: Optional[List[float]],
                      step: int = 10,
                      neighbors: int = 8):
    """
        Calculate the angle at node, e.g. soma, given a gradient field

        Parameters
        ----------
        gradient_path: a file path to the gradient field
        step: ratio to downsample the grid of gradient
        node: a list [x,y,z] to present the node location 

        Returns
        -------
        angle

    """
    if not node:
        node = [0, 0, 0]
    
    with xr.open_dataarray(gradient_path) as gradient:

        extent = step * neighbors // 2
        nx_idx = np.searchsorted(gradient.x, node[0])
        ny_idx = np.searchsorted(gradient.y, node[1])
        gradient_ds = gradient[nx_idx-extent:nx_idx+extent:step,
                                ny_idx-extent:ny_idx+extent:step,
                                :]

        return interpolate_angle_from_gradient(gradient_ds, node)


def main(gradient_path: str,
         swc_path: str,
         node:Optional[List[float]],
         step: int = 10, 
         neighbors: int = 8):
    
    theta = get_upright_angle(gradient_path, node, step, neighbors)
    transform = np.eye(4)
    transform[0:3, 0:3] = aff.rotation_from_angle(theta)

    morph = morphology_from_swc(swc_path)
    soma = morph.get_soma()
    x = soma['x']
    y = soma['y']
    c = np.cos(theta)
    s = np.sin(theta)
    
    transform[0:3,3] = np.asarray([-x * c + y * s + x,
                                  -x * s - y * c + y,
                                  0])
    
    output = {
        'upright_transform_dict': aff.AffineTransform(transform).to_dict(),
        'upright_angle': str(theta)
    }
    return output
        
if __name__ == "__main__":
    
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))
    args.pop("output_json")

    output = main(**args)
    output.update({"inputs": parser.args})

    parser.output(output)