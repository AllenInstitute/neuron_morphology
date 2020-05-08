import os
import json

import boto3

from neuron_morphology.transforms.pia_wm_streamlines.calculate_pia_wm_streamlines import run_streamlines

from harness import step_fns_ecs_harness


s3 = boto3.client("s3")


def collect_inputs(working_bucket, run_prefix, reconstruction_id):

    md_json_key = f"{run_prefix}/{reconstruction_id}.json"
    md_json_response = s3.get_object(Bucket=working_bucket, Key=md_json_key)
    metadata = json.loads(md_json_response["Body"].read())

    return {
        "pia_path_str": metadata["primary_boundaries"]["Pia"]["path"],
        "wm_path_str": metadata["primary_boundaries"]["White_Matter"]["path"],
        "soma_path_str": metadata["primary_boundaries"]["Soma"]["path"],
        "resolution": metadata["primary_boundaries"]["Soma"]["resolution"]  # TODO there should only be one of these
    }


def xarray_to_s3(bucket, key, dataset):
    
    # xarray can only write netcdf3 files directly to bytes, not netcdf4
    tmp_path = key.split("/")[-1]
    dataset.to_netcdf(tmp_path)
    s3.upload_file(Filename=tmp_path, Bucket=bucket, Key=key)

    os.remove(tmp_path)
    return key


def put_outputs(bucket, prefix, depth_field, gradient_field, translation):
    return {
        "translation": translation.tolist(),
        "depth_field_key": xarray_to_s3(
            bucket, f"{prefix}/depth_field.nc", depth_field
        ),
        "gradient_field_key": xarray_to_s3(
            bucket, f"{prefix}/gradient_field.nc", gradient_field
        )
    }


def run_depth_field(token=None):

    reconstruction_id = os.environ["RECONSTRUCTION_ID"]
    working_bucket = os.environ["WORKING_BUCKET"]
    run_prefix = os.environ["RUN_PREFIX"]

    args = collect_inputs(working_bucket, run_prefix, reconstruction_id)
    depth_field, gradient_field, translation = run_streamlines(**args)

    return put_outputs(
        working_bucket,
        run_prefix,
        depth_field, 
        gradient_field, 
        translation
    )


def main():
    step_fns_ecs_harness(run_depth_field)


if __name__ == "__main__":
    main()