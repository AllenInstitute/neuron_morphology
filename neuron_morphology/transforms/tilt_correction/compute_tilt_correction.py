from typing import Dict, Optional, List, Any

import logging
import copy as cp

import numpy as np
from scipy.spatial.distance import euclidean
import pandas as pd
import h5py

from argschema.argschema_parser import ArgSchemaParser
from neuron_morphology.transforms.tilt_correction._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.morphology import Morphology
from neuron_morphology.swc_io import morphology_from_swc
import neuron_morphology.transforms.affine_transform as aff


CCF_SHAPE = (1320, 800, 1140)
CCF_RESOLUTION = 10


def get_tilt_correction(morphology: Morphology,
                        soma_voxel: Dict[str, int],
                        slice_angle_matrix: float,
                        closest_path,
                        ):
    """
        Find the tilt angle between the slice plane and the nearest streamline

        Parameters
        ----------
        morphology: Morphology object
        soma_voxel: soma voxel in ccf {'x': , 'y': , 'z': }
        slice_angle_matrix: 4 x 4 affine matrix of the slice plane
            relative to ccf
        closest_path: 3 x N array of voxel coordinates in closest streamline

        Returns
        -------
        tilt angle correction (radians)

    """

    # Find slice plane vector
    M = slice_angle_matrix[0:3, :]
    a2 = np.dot(M, np.array([0, 0, 0, 1]))
    b2 = np.dot(M, np.array([1, 0, 0, 1]))
    c2 = np.dot(M, np.array([0, 1, 0, 1]))

    norm_vec = np.cross(b2 - a2, c2 - a2)
    norm_unit = norm_vec / euclidean(norm_vec, [0, 0, 0])

    # Find approximate streamline vector
    if euclidean(closest_path[:, 0], soma_voxel) == 0:
        # if soma is at the top, calculate from other end of streamline
        streamline_unit = (soma_voxel - closest_path[:, -1]) /\
            euclidean(soma_voxel, closest_path[:, -1])
    else:
        streamline_unit = (closest_path[:, 0] - soma_voxel) /\
             euclidean(closest_path[:, 0], soma_voxel)

    # determine angle between
    s = np.linalg.norm(np.cross(norm_unit, streamline_unit))
    dp = np.dot(norm_unit, streamline_unit)
    theta = np.arctan2(s, dp)

    tilt_angle = np.pi / 2 - theta

    return tilt_angle


def load_path_ids_and_voxels(ccf_path):
    vi = h5py.File(ccf_path, 'r')

    # initialize
    path_lookup_table = vi['view lookup'][:][np.where(vi['view lookup'][:] > -1)]
    paths = vi['paths'][:]
    vi.close()

    voxel_idxs = []
    path_id_from_voxel_idx = {}

    for path_id in path_lookup_table:
        path = paths[path_id, :]
        path = path[path > 0]
        for voxel in path:
            path_id_from_voxel_idx[voxel] = [path_id]
        voxel_idxs.extend(path)

    return paths, path_id_from_voxel_idx, voxel_idxs


def find_closest_path_id(soma_voxel: Dict[str, int],
                         path_id_from_voxel_idx: Dict[int, int],
                         voxel_idxs: List[int]):

    voxels = np.array(np.unravel_index(voxel_idxs, CCF_SHAPE))
    delta = voxels - np.reshape(soma_voxel, (3, 1))
    distances = np.linalg.norm(delta, axis=0)
    min_voxel = voxels[:, distances.argmin()]
    min_voxel_idx = np.ravel_multi_index(min_voxel, CCF_SHAPE)
    closest_path_id = path_id_from_voxel_idx[min_voxel_idx]

    return closest_path_id


def determine_slice_flip(morphology: Morphology,
                         soma_marker: Dict,
                         slice_image_flip: bool):
    """
        Determines whether the tilt correction should be positive or negative

        Parameters
        ----------
        morphology: Morphology object
        soma_marker: soma marker dictionary from reconstruction marker file
        slice_image_flip: indicates whether the image was flipped relative
                          to the slice

        Returns
        -------
        flip_toggle -1 or 1 to be multiplied against tilt correction
    """

    flip_toggle = 1

    morph_soma = morphology.get_soma()
    if (soma_marker['z'] - morph_soma['z']) > 0:
        flip_toggle = -1

    if flip_toggle == 1 and not slice_image_flip:
        flip_toggle *= -1

    return flip_toggle


def get_soma_marker_from_marker_file(marker_path: str):
    col_names = ['x', 'y', 'z', 'radius', 'shape', 'name',
                 'comment', 'color_r', 'color_g', 'color_b']
    markers = pd.read_csv(marker_path, sep=',', comment='#',
                          header=None, names=col_names)
    soma_marker = markers.loc[markers['name'] == 30].to_dict('r')
    return soma_marker[0]


def run_tilt_correction(
        swc_path: str,
        marker_path: str,
        ccf_soma_location: Dict,
        slice_transform: aff.AffineTransform,
        slice_image_flip: bool,
        ccf_path: str):

    morph = morphology_from_swc(swc_path)

    soma_marker = get_soma_marker_from_marker_file(marker_path)

    (paths, path_id_from_voxel_idx, voxel_idxs) \
        = load_path_ids_and_voxels(ccf_path)

    soma_voxel = (int(ccf_soma_location["x"] // CCF_RESOLUTION),
                  int(ccf_soma_location["y"] // CCF_RESOLUTION),
                  int(ccf_soma_location["z"] // CCF_RESOLUTION))

    closest_path_id = find_closest_path_id(soma_voxel,
                                           path_id_from_voxel_idx,
                                           voxel_idxs)

    closest_path = paths[closest_path_id]
    closest_path = closest_path[closest_path > 0]
    closest_path_coords = np.array(np.unravel_index(closest_path, CCF_SHAPE))

    tilt = get_tilt_correction(morph,
                               soma_voxel,
                               slice_transform.affine,
                               closest_path_coords)

    flip_toggle = determine_slice_flip(morph, soma_marker, slice_image_flip)

    tilt = tilt * flip_toggle

    transform = aff.affine_from_transform(
                    aff.rotation_from_angle(tilt, axis=0))

    output = {
        'tilt_transform_dict': aff.AffineTransform(transform).to_dict(),
        'tilt_correction': str(tilt)
    }
    return output


def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    if 'slice_transform_dict' in args:
        slice_transform = aff.AffineTransform.from_dict(
            args['slice_transform_dict'])
    elif 'slice_transform_list' in args:
        slice_transform = aff.AffineTransform.from_list(
            args['slice_transform_list'])
    else:
        raise ValueError('must provide either an slice_transform_dict '
                         'or an slice_transform_list')

    output = run_tilt_correction(
        args["swc_path"],
        args["marker_path"],
        args["ccf_soma_location"],
        slice_transform,
        args["slice_image_flip"],
        args["ccf_path"],
    )
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__":
    main()
