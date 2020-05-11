import os
import json
from typing import Dict, Any, Union

import boto3
import xarray as xr
import numpy as np

from neuron_morphology.transforms.pia_wm_streamlines.calculate_pia_wm_streamlines import run_streamlines

from harness import step_fns_ecs_harness


s3 = boto3.client("s3")


DatasetLike = Union[xr.Dataset, xr.DataArray]


def collect_inputs(
        working_bucket: str, 
        run_prefix: str, 
        reconstruction_id: str
) -> Dict[str, Any]:
    """Gather from AWS the inputs required to run the depth field module.

    Parameters
    ----------
    working_bucket : The name of this pipeline's working bucket
    run_prefix : This run's resources (within the working bucket) have keys 
        beginning with this prefix.
    reconstruction_id : identifier for the reconstruction being processed

    Returns
    -------
    A dict with string keys:
        pia_path_str : alternating x,y coordinates of the pia surface
        wm_path_str : alternating x,y coordinates of the white matter surface
        soma_path_str : alternating x,y coordinates of the soma boundary
        resolution : of these paths, in microns
    """

    md_json_key = f"{run_prefix}/{reconstruction_id}.json"
    md_json_response = s3.get_object(Bucket=working_bucket, Key=md_json_key)
    metadata = json.loads(md_json_response["Body"].read())

    return {
        "pia_path_str": metadata["primary_boundaries"]["Pia"]["path"],
        "wm_path_str": metadata["primary_boundaries"]["White_Matter"]["path"],
        "soma_path_str": metadata["primary_boundaries"]["Soma"]["path"],
        "resolution": metadata["primary_boundaries"]["Soma"]["resolution"]  # TODO module expects single resolution
    }


def xarray_to_s3(bucket: str, key: str, dataset: DatasetLike):
    """Store an xarray dataset in an s3 bucket as netcdf4

    Parameters
    ----------
    bucket : name of the bucket in which to store this dataset
    key : at which to store the dataset
    dataset : The dataset to store

    Returns
    -------
    key : the argued key

    Notes
    -----
    xarray can only write netcdf3 files directly to bytes, not netcdf4, so 
    we must write to "disk" temporarily and send that.
    """
    
    tmp_path = key.split("/")[-1]
    dataset.to_netcdf(tmp_path)
    s3.upload_file(Filename=tmp_path, Bucket=bucket, Key=key)

    os.remove(tmp_path)
    return key


def put_outputs(
        bucket: str, 
        prefix: str, 
        depth_field: DatasetLike, 
        gradient_field: DatasetLike, 
        translation: np.ndarray
) -> Dict[str, Any]:
    """Write this module's xarray outputs to s3 & prepare its step functions 
    response.

    Parameters
    ----------
    bucket : the name of the bucket to which the xarrays will be written
    prefix : keys at which the xarrays are stored will begin with this prefix
    depth_field : the depth field array
    gradient_field : the gradient of the depth field 
    translation : the opposite of the translation applied to move the soma to 
        the origin. 

    Returns
    -------
    Outputs to send back to step functions. These are:
        translation : a 2-list of floats
        depth_field_key : s3 key of the depth field
        gradient_field_key : s3 key of the gradient field 
    """

    return {
        "translation": translation.tolist(),
        "depth_field_key": xarray_to_s3(
            bucket, f"{prefix}/depth_field.nc", depth_field
        ),
        "gradient_field_key": xarray_to_s3(
            bucket, f"{prefix}/gradient_field.nc", gradient_field
        )
    }


def run_depth_field(token: Optional[str] = None):
    """Entry point for running the streamlines step from a 
    step-functions-managed ECS instance
    """

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