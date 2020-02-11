import sys
import os

from typing import List, Tuple

import numpy as np
from scipy.interpolate import griddata
import xarray as xr

from argschema import ArgSchemaParser

from neuron_morphology.transforms.pia_wm_streamlines._schemas import (
    PiaWmStreamlineSchema, OutputParameters)
from neuron_morphology.transforms.streamline import generate_laplace_field


def convert_path_str_to_list(path_str: str,
                             resolution: float = 1.0
                             ) -> List[Tuple[float, float]]:

    vals = path_str.split(',')

    list_coords = []
    for x, y in zip(vals[0::2], vals[1::2]):
        list_coords.append((float(x) * resolution, float(y) * resolution))

    return list_coords


def main():
    mod = ArgSchemaParser(schema_type=PiaWmStreamlineSchema,
                          output_schema_type=OutputParameters)
    args = mod.args

    pia_path = convert_path_str_to_list(args['pia_path_str'], args['resolution'])
    wm_path = convert_path_str_to_list(args['wm_path_str'], args['resolution'])

    soma_center = np.asarray([0, 0])
    if 'soma_path_str' in args:
        soma_path = convert_path_str_to_list(args['soma_path_str'],
                                             args['resolution'])
        soma_center = np.mean(soma_path, axis=0)
        pia_path = [(x - soma_center[0], y - soma_center[1])
                    for (x, y) in pia_path]
        wm_path = [(x - soma_center[0], y - soma_center[1])
                   for (x, y) in wm_path]

    (u, grad_u, mesh, mesh_coords, mesh_values, mesh_gradients) = \
        generate_laplace_field(pia_path,
                               wm_path,
                               mesh_res=args['mesh_res'],
                               top_value=args['pia_fixed_value'],
                               bottom_value=args['wm_fixed_value'],
                               eps_bounds=1e-8)

    x = [coord[0] for coord in mesh_coords]
    y = [coord[1] for coord in mesh_coords]
    xx = np.arange(min(x)-1, max(x)+1, 1)
    yy = np.arange(min(y)-1, max(y)+1, 1)

    grid_x, grid_y = np.meshgrid(xx, yy)
    grid_u = griddata((x, y),
                      np.asarray(mesh_values),
                      (grid_x, grid_y),
                      method='cubic')
    grid_grad_u = griddata((x, y),
                           np.asarray(mesh_gradients),
                           (grid_x, grid_y),
                           method='cubic')

    depth_field = xr.DataArray(
        data=grid_u,
        dims=['x', 'y'],
        coords={'x': xx, 'y': yy})
    gradient_field = xr.DataArray(
        data=grid_grad_u,
        dims=['x', 'y', 'dim'],
        coords={'x': xx, 'y': yy, 'dim': ['dx', 'dy']})

    depth_field_file = os.path.join(args['output_dir'],
                                    'depth_field.nc')
    gradient_field_file = os.path.join(args['output_dir'],
                                       'gradient_field.nc')
    # could use to_dict() instead
    depth_field.to_netcdf(depth_field_file)
    gradient_field.to_netcdf(gradient_field_file)

    output = {
        'inputs': args,
        'translation': -soma_center,
        'depth_field_file': depth_field_file,
        'gradient_field_file': gradient_field_file,
    }

    mod.output(output)


if __name__ == '__main__':
    sys.exit(main())
