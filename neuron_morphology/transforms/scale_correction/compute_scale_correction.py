from typing import Dict, Optional, List, Any, Union

import logging
import copy as cp

import numpy as np
import pandas as pd
import warnings
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
        Estimate a scale factor to correct the reconstructed morphology
        for slice shrinkage

        Prior to reconstruction, the slice shrinks due to evaporation.
        This is most notable in the z axis, which is the slice thickness.

        To correct for shrinkage we compare soma depth within the slice
        obtained soon after cutting the slice to the fixed_soma_depth obtained
        during the reconstruction. Then the scale correction is estimated as:
        scale  = soma_depth / fixed_soma_depth.
        This is sensible as long as the z span of the corrected reconstruction
        is contained  within the slice thickness. Thus we also estimate
        the maximum scale correction as:
        scale_max  = cut_thickness / z_span,
        and take the smaller of scale and scale_max


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
    soma_morph_z = morphology.get_soma()['z']
    fixed_depth = np.abs(soma_morph_z - soma_marker_z)
    scale = soma_depth / fixed_depth

    node_z = [node['z'] for node in morphology.nodes()]
    z_range = np.max(node_z) - np.min(node_z)
    scale_max = cut_thickness / z_range

    if scale > scale_max:
        scale = scale_max
        warnings.warn(f"Shrinkage scale correction factor: {scale} "
                      f"exceeded the max allowed value: {scale_max}. "
                      f"Will correct for shrinkage using the maximum value."
                      )

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
        cut_thickness: float):


    scale_correction = estimate_scale_correction(morphology,
                                      soma_depth,
                                      soma_marker_z,
                                      cut_thickness)

    scale_transform = aff.affine_from_transform(
        [[1, 0, 0],
         [0, 1, 0],
         [0, 0, scale_correction]]
    )
    at = aff.AffineTransform(scale_transform)
    morphology_scaled = at.transform_morphology(morphology,
                                                scale_radius=False)

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
