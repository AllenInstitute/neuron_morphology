import os
import json
from io import BytesIO

import logging

import boto3

from neuron_morphology.transforms.tilt_correction.compute_tilt_correction \
    import (run_tilt_correction, read_soma_marker, load_ccf_data)
from neuron_morphology.swc_io import (morphology_from_swc, morphology_to_swc)
from neuron_morphology.transforms.affine_transform \
    import (AffineTransform)

from harness import step_fns_ecs_harness


s3 = boto3.client("s3")
logger = logging.getLogger('simple_example')
logger.setLevel(logging.DEBUG)


def collect_inputs(working_bucket, run_prefix,
                   reconstruction_id, upright_swc_key):

    md_json_key = f"{run_prefix}/{reconstruction_id}.json"
    md_json_response = s3.get_object(Bucket=working_bucket, Key=md_json_key)
    metadata = json.load(md_json_response["Body"])

    marker_key = f"{run_prefix}/{metadata['marker_file']}"
    ccf_key = 'top_view_paths_10.h5'

    # Use input swc for now
    upright_swc_key = f"{run_prefix}/{metadata['swc_file']}"

    logger.debug('Collecting S3 Objects')
    swc_response = s3.get_object(Bucket=working_bucket,
                                 Key=upright_swc_key,
                                 )

    marker_response = s3.get_object(Bucket=working_bucket,
                                    Key=marker_key,
                                    )
    ccf_response = s3.get_object(Bucket=working_bucket,
                                 Key=ccf_key,
                                 )

    logger.debug('Loading morphology')
    morphology = morphology_from_swc(swc_response["Body"])
    logger.debug('Loading marker file')
    soma_marker = read_soma_marker(marker_response["Body"])
    logger.debug('Loading ccf_data')
    ccf_data = load_ccf_data(BytesIO(ccf_response["Body"].read()))
    logger.debug('Loading slice_transform')
    slice_transform = AffineTransform.from_dict(metadata['slice_transform'])

    return {
        'morphology': morphology,
        'soma_marker': soma_marker,
        'ccf_soma_location': metadata['ccf_soma_location'],
        'slice_transform': slice_transform,
        'slice_image_flip': metadata['slice_image_flip'],
        'ccf_data': ccf_data,
    }


def put_outputs(bucket, prefix,
                tilt_correction, tilt_transform, transformed_morphology):

    transformed_swc_key = f"{prefix}/tilt_corrected.swc"
    logger.debug('Creating tmp swc file')
    tmp_path = transformed_swc_key.split("/")[-1]
    morphology_to_swc(transformed_morphology, tmp_path)
    logger.debug('Uploading transformed swc')
    s3.upload_file(Filename=tmp_path, Bucket=bucket, Key=transformed_swc_key)
    logger.debug('Removing tmp swc file')
    os.remove(tmp_path)

    return {
        'tilt_correction': tilt_correction,
        'tilt_transform': tilt_transform.to_dict(),
        'corrected_swc': transformed_swc_key
    }


def run_tilt(token=None):
    reconstruction_id = os.environ["RECONSTRUCTION_ID"]
    working_bucket = os.environ["WORKING_BUCKET"]
    run_prefix = os.environ["RUN_PREFIX"]
    upright_swc_key = os.environ["UPRIGHT_SWC_KEY"]

    logger.debug('Collecting inputs')
    args = collect_inputs(working_bucket,
                          run_prefix,
                          reconstruction_id,
                          upright_swc_key)
    logger.debug('Running tilt correction')
    (tilt_correction, tilt_transform) = run_tilt_correction(**args)
    logger.debug('Completed tilt correction')
    logger.debug('Transforming morphology')
    tf_morph = tilt_transform.transform_morphology(args['morphology'])

    logger.debug('Putting outputs')
    return put_outputs(working_bucket, run_prefix,
                       tilt_correction, tilt_transform, tf_morph)


def main():
    step_fns_ecs_harness(run_tilt)


if __name__ == "__main__":
    main()
