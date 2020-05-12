import os
import json
import boto3
from neuron_morphology.transforms.scale_correction import compute_scale_correction
from neuron_morphology.swc_io import morphology_from_swc
from typing import Dict, Any

from harness import step_fns_ecs_harness

s3 = boto3.client("s3")


def collect_inputs(
    working_bucket: str,
    run_prefix: str,
    reconstruction_id: int) -> Dict[str,Any]:
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

    input_json_key = f"{reconstruction_id}/{run_prefix}/{reconstruction_id}.json"
    input_json_response = s3.get_object(Bucket=working_bucket,
                                        Key=input_json_key
                                        )

    input_data = json.load(input_json_response["Body"])

    swc_key = f"{reconstruction_id}/{run_prefix}/{input_data['swc_file']}"
    soma_marker_key = f"{reconstruction_id}/{run_prefix}/{input_data['marker_file']}"


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



def main(token=None):

    working_bucket = os.environ.get("WORKING_BUCKET")
    reconstruction_id = os.environ.get("RECONSTRUCTION_ID")
    run_prefix = os.environ.get("RUN_PREFIX")
    inputs = collect_inputs(working_bucket, run_prefix, reconstruction_id)
    outputs = compute_scale_correction.run_scale_correction(**inputs)

    return outputs

if __name__ == "__main__":
    step_fns_ecs_harness(main)
