import os
import json
from typing import Optional

import matplotlib.pyplot as plt
import boto3

from neuron_morphology.morphology import Morphology
from neuron_morphology.swc_io import morphology_from_swc

from harness import step_fns_ecs_harness


s3 = boto3.client("s3")


def collect_morphology(bucket: str,
                       swc_key: str):
    swc_response = s3.get_object(Bucket=bucket,
                                 Key=swc_key,
                                 )
    return morphology_from_swc(swc_response["Body"])


def morphology_png_to_s3(bucket: str,
                         key: str,
                         morphology: Morphology):

    tmp_path = key.split("/")[-1]

    nodes = morphology.nodes()
    x = [node['x'] for node in nodes]
    y = [node['y'] for node in nodes]
    z = [node['z'] for node in nodes]

    fig, ax = plt.subplots(1, 2)
    ax[0].scatter(x, y, s=0.1)
    ax[0].set_title('x-y view')
    ax[1].scatter(z, y, s=0.1)
    ax[1].set_title('z-y view')
    fig.suptitle(tmp_path[:-4], fontsize=16)
    fig.savefig(tmp_path)

    s3.upload_file(Filename=tmp_path, Bucket=bucket, Key=key)
    os.remove(tmp_path)
    return key


def run_create_images(token: Optional[str] = None):
    """Entry point for running the image generation step from a 
    step-functions-managed ECS instance
    """

    reconstruction_id = os.environ["RECONSTRUCTION_ID"]
    working_bucket = os.environ["WORKING_BUCKET"]
    run_prefix = os.environ["RUN_PREFIX"]

    md_json_key = f"{run_prefix}/{reconstruction_id}.json"
    md_json_response = s3.get_object(Bucket=working_bucket, Key=md_json_key)
    metadata = json.load(md_json_response["Body"])
    landing_swc_key = f"{run_prefix}/{metadata['swc_file']}"

    keys = {'landing': landing_swc_key,
            'scale': os.environ["SCALE_SWC_KEY"],
            'upright': os.environ["UPRIGHT_SWC_KEY"],
            }

    tilt_swc_key = os.environ["TILT_SWC_KEY"]
    if tilt_swc_key is not None:
        keys.update({'tilt': tilt_swc_key})

    png_keys = {}
    for name, key in keys:
        morph = collect_morphology(working_bucket, key)
        png_key = f"{run_prefix}/{name}.png"
        morphology_png_to_s3(working_bucket, png_key, morph)
        png_keys[f"{name}_png_key"] = png_key
    return png_keys


def main():
    step_fns_ecs_harness(run_create_images)


if __name__ == "__main__":
    main()
