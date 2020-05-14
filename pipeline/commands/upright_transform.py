import os
import json
import xarray as xr

from typing import Dict, Any, Union, Optional

import boto3

import numpy as np
from neuron_morphology.swc_io import morphology_from_swc
import neuron_morphology.transforms.affine_transform as aff
from neuron_morphology.transforms.upright_angle.compute_angle import get_upright_angle, calculate_transform
from neuron_morphology.swc_io import morphology_to_swc
from neuron_morphology.morphology import Morphology

from harness import step_fns_ecs_harness
from scale_correction import morphology_to_s3


s3 = boto3.client("s3")


def collect_inputs(
        working_bucket: str, 
        run_prefix: str, 
        morphology_scaled_key: str,
        gradient_field_key: str
 ) -> Dict[str, Any]:
    """
    Gather from AWS the inputs required to run the depth field module.

    Parameters
    ----------
    working_bucket : The name of this pipeline's working bucket
    run_prefix : This run's resources (within the working bucket) have keys 
        beginning with this prefix.
    morphology_scaled_key : identifier for the scaled corrected morphology
    gradient_field_key: identifier for the gradient field

    Returns
    -------
    morphology : Morphology object of scale corrected reconstruction
    gradient_field : xarray object of the gradient field
    """

    # boto3 get bytes from s3 working buckets
    gradient_field_response = s3.get_object(Bucket=working_bucket, Key=gradient_field_key)
    gradient_field = xr.open_dataarray(gradient_field_response["Body"].read())

    swc_file_response = s3.get_object(Bucket=working_bucket, Key=morphology_scaled_key)
    morphology = morphology_from_swc(swc_file_response["Body"])

    return morphology, gradient_field

def put_outputs(
        bucket: str, 
        prefix: str, 
        upright_transform: Dict[str, float], 
        upright_angle: str, 
        upright_morphology: Morphology
) -> Dict[str, Any]:
    """Write this module's outputs to s3 & prepare its step functions 
    response.

    Parameters
    ----------
    bucket : the name of the bucket to which the upright transform outputs will be written
    prefix : keys at which the upright transform outputs are stored will begin with this prefix
    upright_transform : the dict of the upright transform matrix
    upright_angle : the angle of the upright direction 
    upright_morphology : the upright transformed morphology. 

    Returns
    -------
    Outputs to send back to step functions. These are:
        upright_transform_dict : the upright transform matrix
        upright_angle : the upright angle
        upright_morphology_key : s3 key of the upright transformed morphology 
    """

    return {
        'upright_transform_dict': upright_transform,
        'upright_angle': upright_angle,
        "upright_swc_key": morphology_to_s3(
            bucket, f"{prefix}/upright_morphology.swc", upright_morphology
        )

    }


def run_upright_transform(token: Optional[str] = None):
    """Entry point for running the upright transform step from a 
    step-functions-managed ECS instance
    """

    working_bucket = os.environ["WORKING_BUCKET"]
    run_prefix = os.environ["RUN_PREFIX"]
    gradient_field_key = os.environ["GRADIENT_FIELD_KEY"]
    morphology_scaled_key = os.environ["MORPHOLOGY_SCALED_KEY"]
 
    morphology, gradient_field = collect_inputs(working_bucket, run_prefix, morphology_scaled_key, gradient_field_key)

    # find the upright direction at the soma location
    outputs = calculate_transform(gradient_field, morphology)

    # apply affine transform
    upright_morphology = outputs["upright_transform"].transform_morphology(morphology, clone=True)

    return put_outputs(
        working_bucket,
        run_prefix,
        outputs["upright_transform"].to_dict(),
        outputs["upright_angle"],
        upright_morphology
    )


def main():
    step_fns_ecs_harness(run_upright_transform)


if __name__ == "__main__":
    main()
