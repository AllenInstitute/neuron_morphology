from typing import Dict, Optional, List, Any, Union

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
        morphology: Morphology,
        soma_marker_z: float,
        soma_depth: float,
        cut_thickness: Optional[float]):


    scale_correction = estimate_scale_correction(morphology,
                                      soma_depth,
                                      soma_marker_z,
                                      cut_thickness=cut_thickness)

    scale_transform = aff.affine_from_transform(
        [[1, 0, 0],
         [0, 1, 0],
         [0, 0, scale_correction]]
    )
    at = aff.AffineTransform(scale_transform)
    morphology_scaled = at.transform_morphology(morphology)

    return {
        "morphology_scaled": morphology_scaled,
        "scale_transform": at.to_dict(),
        "scale_correction": scale_correction,
    }

def collect_inputs(args: Dict[str,Any]) -> Dict[str,Any]:
    """

    Parameters
    ----------
    args: dict of InputParameters

    Returns
    -------
    dict with string keys:
        morphology: Morphology object
        soma_marker_z: z value from the marker file
        soma_depth: soma depth
        cut_thickness: slice thickness
    """
    morphology = morphology_from_swc(args["swc_path"])
    soma_marker = get_soma_marker_from_marker_file(args["marker_path"])
    soma_depth = args["soma_depth"]
    cut_thickness = args["cut_thickness"]

    return {
        "morphology": morphology,
        "soma_marker_z": soma_marker["z"],
        "soma_depth": soma_depth,
        "cut_thickness": cut_thickness,
    }

def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    inputs = collect_inputs(args)
    outputs = run_scale_correction(**inputs)
    outputs.pop("morphology_scaled")

    outputs.update({"inputs": parser.args})
    parser.output(outputs)


if __name__ == "__main__":
    main()
