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


def get_tilt_correction(morphology: Morphology,
                        soma_marker: Dict,
                        slice_angle: float,
                        streamlines,
                        ):
    """
        Estimate a scale factor correction from recorded cell depth

        Parameters
        ----------
        morphology: Morphology object
        soma_marker: soma marker from revised marker file
        slice_angle: angle the slice was cut at about x axis
        streamlines: data structure containing ccf streamlines

        Returns
        -------
        tilt angle correction

    """
    
    return tilt_angle


def get_soma_marker_from_marker_file(marker_path: str):
    col_names = ['x', 'y', 'z', 'radius', 'shape', 'name',
                 'comment', 'color_r', 'color_g', 'color_b']
    markers = pd.read_csv(marker_path, sep=',', comment='#',
                          header=None, names=col_names)
    soma_marker = markers.loc[markers['name'] == 30].to_dict('r')
    return soma_marker[0]


def load_streamlines(ccf_path):
    return streamlines


def run_tilt_correction(
        swc_path: str,
        marker_path: str,
        slice_angle: float,
        ccf_path: str):

    morph = morphology_from_swc(swc_path)
    soma_marker = get_soma_marker_from_marker_file(marker_path)
    streamlines = load_streamlines(ccf_path)

    tilt = get_tilt_correction(morph,
                               soma_marker,
                               slice_angle,
                               streamlines)

    transform = aff.affine_from_transform(
                    aff.rotation_from_angle(tilt, axis=0))

    output = {
        'tilt_transform_dict': aff.AffineTransform(transform).to_dict(),
        'tilt_angle': str(tilt)
    }
    return output


def main():
    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = run_tilt_correction(
        args["swc_path"],
        args["marker_path"],
        args["slice_transform_list"],
        args["ccf_path"],
    )
    output.update({"inputs": parser.args})

    parser.output(output)


if __name__ == "__main__":
    main()