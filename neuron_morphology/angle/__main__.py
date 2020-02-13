from typing import Dict
import logging
import copy as cp

import numpy as np

from argschema.argschema_parser import ArgSchemaParser
from neuron_morphology.angle._schemas import (
    InputParameters, OutputParameters)

from neuron_morphology.morphology import Morphology
from neuron_morphology.transforms.affine_transform import rotation_from_angle
from neuron_morphology.angle.compute_angle import ComputeAngle

def main(
    swc_path: str,
    gradient_path: str,
    decimate: int
) -> Dict:

    upright_angle = ComputeAngle().compute(gradient_path, [0,0], decimate)

    affine_transform = np.identity(4)
    rotation = rotation_from_angle(upright_angle)
    affine_transform[0:3,0:3] = rotation

    return {
        "angle": upright_angle,
        "transform": affine_transform.tolist()
    }

if __name__ == "__main__":

    parser = ArgSchemaParser(
        schema_type=InputParameters,
        output_schema_type=OutputParameters
    )

    args = cp.deepcopy(parser.args)
    logging.getLogger().setLevel(args.pop("log_level"))

    output = main(**args)
    output.update({"inputs": parser.args})

    parser.output(output)