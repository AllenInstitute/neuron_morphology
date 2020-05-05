from typing import Dict, Optional, List, Any

import logging
import copy as cp

import numpy as np
import pandas as pd

from argschema.argschema_parser import ArgSchemaParser
from neuron_morphology.transforms.scale_correction._schemas import (
    InputParameters, OutputParameters)
from neuron_morphology.morphology import Morphology
from neuron_morphology.swc_io import morphology_from_swc
import neuron_morphology.transforms.affine_transform as aff


def estimate_scale_correction(morphology: Morphology,
                              soma_depth: float,
                              soma_marker_z: float,
                              cut_thickness: Optional[float] = 350):
    """
        Estimate a scale factor correction from recorded soma depth

        Prior to reconstruction, the slice looses thickness do to evaporation
        This is most notable in the z axis, which is the slice thickness
        It is necessary to correct the reconstructions for this shrinkage

        Parameters
        ----------
        morphology: Morphology object
        soma_depth: recorded depth of the soma when it was sliced
        soma_marker_z: soma marker z value from revised marker file
                       (z is on the slice surface for the marker file)
        cut_thickness: thickness of the cut slice

        Returns
        -------
        scale factor correction

    """
    z_values = [node['z'] for node in morphology.nodes()]
    max_z_extent = np.max(z_values) - np.min(z_values)

    soma = morphology.get_soma()
    fixed_depth = np.abs(soma['z'] - soma_marker_z)

    scale = soma_depth / fixed_depth

    if (scale * max_z_extent) > cut_thickness:
        # Morphology can't be larger than the slice,
        # rescale so max_z_extent = cut_thickness
        return cut_thickness / max_z_extent

    return scale


def get_soma_marker_from_marker_file(marker_path: str):
    col_names = ['x', 'y', 'z', 'radius', 'shape', 'name',
                 'comment', 'color_r', 'color_g', 'color_b']
    markers = pd.read_csv(marker_path, sep=',', comment='#',
                          header=None, names=col_names)
    soma_marker = markers.loc[markers['name'] == 30].to_dict('r')
    return soma_marker[0]


def run_scale_correction(
        swc_path: str,
        marker_path: str,
        soma_depth: float,
        cut_thickness: Optional[float]):

    morph = morphology_from_swc(swc_path)
    soma_marker = get_soma_marker_from_marker_file(marker_path)

    scale = estimate_scale_correction(morph,
                                      soma_depth,
                                      soma_marker['z'],
                                      cut_thickness=cut_thickness)

    transform = aff.affine_from_transform([[1, 0, 0],
                                           [0, 1, 0],
                                           [0, 0, scale]])

    output = {
        'scale_transform_dict': aff.AffineTransform(transform).to_dict(),
        'scale_correction': str(scale)
    }
    return output


def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = run_scale_correction(
        args["swc_path"],
        args["marker_path"],
        args["soma_depth"],
        args["cut_thickness"],
    )
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__":
    main()