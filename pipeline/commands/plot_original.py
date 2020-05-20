import os
import json
from typing import Optional

import boto3

from command_utils import collect_morphology, morphology_png_to_s3
from harness import step_fns_ecs_harness

s3 = boto3.client("s3")


def plot_original(token: Optional[str] = None):
    reconstruction_id = os.environ["RECONSTRUCTION_ID"]
    working_bucket = os.environ["WORKING_BUCKET"]
    run_prefix = os.environ["RUN_PREFIX"]

    input_json_key = f"{run_prefix}/{reconstruction_id}.json"
    input_json_response = s3.get_object(Bucket=working_bucket,
                                        Key=input_json_key
                                        )

    input_data = json.load(input_json_response["Body"])

    swc_key = f"{run_prefix}/{input_data['swc_file']}"
    morphology = collect_morphology(working_bucket, swc_key)
    return {
            "original_png_key": morphology_png_to_s3(
                working_bucket,
                f"{run_prefix}/original_morphology.png",
                morphology)
            }


def main():
    step_fns_ecs_harness(plot_original)


if __name__ == "__main__":
    main()
