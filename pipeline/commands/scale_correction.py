import os
import json
import boto3
from neuron_morphology.transforms.scale_correction import compute_scale_correction
from neuron_morphology.swc_io import morphology_from_swc
from typing import Dict, Any
from neuron_morphology.morphology import Morphology

from command_utils import morphology_to_s3, morphology_png_to_s3
from harness import step_fns_ecs_harness

s3 = boto3.client("s3")


def collect_inputs(
        working_bucket: str,
        run_prefix: str,
        reconstruction_id: int) -> Dict[str, Any]:
    """
    Gather from AWS the inputs  required to run the scale correction module.

    Parameters
    ----------
    working_bucket : str
        name of this pipeline's working bucket
    run_prefix : str
        identifier for the run
    reconstruction_id: int
        identifier for reconstruction being processed

    Returns
    -------
    dict with string keys:
        morphology: Morphology object
        soma_marker_z: z value from the marker file
        soma_depth: soma depth
        cut_thickness: slice thickness

    """

    input_json_key = f"{run_prefix}/{reconstruction_id}.json"
    input_json_response = s3.get_object(Bucket=working_bucket,
                                        Key=input_json_key
                                        )

    input_data = json.load(input_json_response["Body"])

    swc_key = f"{run_prefix}/{input_data['swc_file']}"
    soma_marker_key = f"{run_prefix}/{input_data['marker_file']}"

    swc_response = s3.get_object(Bucket=working_bucket,
                                 Key=swc_key,
                                 )

    soma_marker_response = s3.get_object(Bucket=working_bucket,
                                         Key=soma_marker_key,
                                         )

    morphology = morphology_from_swc(swc_response["Body"])

    soma_marker = compute_scale_correction.get_soma_marker_from_marker_file(soma_marker_response["Body"])

    return {
        "morphology": morphology,
        "soma_marker_z": soma_marker["z"],
        "soma_depth": input_data["cell_depth"],
        "cut_thickness": input_data["cut_thickness"],
    }


def put_outputs(
        bucket: str,
        prefix: str,
        morphology: Morphology,
        transform: Dict,
        scale_correction: float,
) -> Dict[str, Any]:
    """Write this module's scaled_morphology output to s3 & prepare its step functions
    response.

    Parameters
    ----------
    bucket : the name of the bucket to which the xarrays will be written
    prefix : keys at which the xarrays are stored will begin with this prefix
    morphology : scaled morphology
    transform : dict of transform coefficients,
    scale_correction: float of scale factor

    Returns
    -------
    Outputs to send back to step functions. These are:
        scale_transform : Dict[str,float]
        scaled_swc_key : s3 key of the scaled_morphology
        scaled_png_key: s3 key of the scaled morphology png
    """
    return {
        "scale_transform": transform,
        "scale_correction": scale_correction,
        "scaled_swc_key": morphology_to_s3(
            bucket,
            f"{prefix}/scaled_morphology.swc",
            morphology
        ),
        "scaled_png_key": morphology_png_to_s3(
            bucket,
            f"{prefix}/scaled_morphology.png",
            morphology
        )
    }


def main(token=None):

    working_bucket = os.environ.get("WORKING_BUCKET")
    reconstruction_id = os.environ.get("RECONSTRUCTION_ID")
    run_prefix = os.environ.get("RUN_PREFIX")

    inputs = collect_inputs(working_bucket, run_prefix, reconstruction_id)
    outputs = compute_scale_correction.run_scale_correction(**inputs)

    return put_outputs(
        working_bucket,
        run_prefix,
        outputs["morphology_scaled"],
        outputs["scale_transform"],
        outputs["scale_correction"],
    )

if __name__ == "__main__":
    step_fns_ecs_harness(main)
