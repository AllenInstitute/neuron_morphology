from typing import Dict
import logging

import numpy as np

from argschema.argschema_parser import ArgSchemaParser

from neuron_morphology.angle._schemas import (
    InputParameters, OutputParameters)


def main(
    swc_path: str,
    gradient_path: str,
    decimate: int
) -> Dict:

    angle: float = do_some_stuff_to_get_angle(swc_path, gradient_path, decimate)
    transform: np.ndarray = do_some_stuff_to_get_transform(angle)

    return {
        "angle": angle,
        "transform": transform.tolist()
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