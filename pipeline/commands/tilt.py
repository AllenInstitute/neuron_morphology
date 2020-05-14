import os
import json
from io import BytesIO

import boto3

from neuron_morphology.transforms.tilt_correction.compute_tilt_correction \
    import (run_tilt_correction, read_soma_marker, load_ccf_data)
from neuron_morphology.swc_io import (morphology_from_swc, morphology_to_swc)
from neuron_morphology.transforms.affine_transform \
    import (AffineTransform)

from harness import step_fns_ecs_harness
from scale_correction import morphology_to_s3


s3 = boto3.client("s3")


def collect_inputs(working_bucket: str,
                   run_prefix: str,
                   reconstruction_id: int,
                   upright_swc_key: str):

    md_json_key = f"{run_prefix}/{reconstruction_id}.json"
    md_json_response = s3.get_object(Bucket=working_bucket, Key=md_json_key)
    metadata = json.load(md_json_response["Body"])

    marker_key = f"{run_prefix}/{metadata['marker_file']}"
    ccf_key = 'top_view_paths_10.h5'

    swc_response = s3.get_object(Bucket=working_bucket,
                                 Key=upright_swc_key,
                                 )

    marker_response = s3.get_object(Bucket=working_bucket,
                                    Key=marker_key,
                                    )
    ccf_response = s3.get_object(Bucket=working_bucket,
                                 Key=ccf_key,
                                 )

    morphology = morphology_from_swc(swc_response["Body"])
    soma_marker = read_soma_marker(marker_response["Body"])
    ccf_data = load_ccf_data(BytesIO(ccf_response["Body"].read()))

    ccf_soma_location = dict(zip(['x', 'y', 'z'], metadata["ccf_soma_xyz"]))
    slice_transform = AffineTransform.from_list(metadata['slice_transform'])

    return {
        'morphology': morphology,
        'soma_marker': soma_marker,
        'ccf_soma_location': ccf_soma_location,
        'slice_transform': slice_transform,
        'slice_image_flip': metadata['slice_image_flip'],
        'ccf_data': ccf_data,
    }


def put_outputs(bucket,
                prefix,
                tilt_correction,
                tilt_transform,
                tilted_morphology):

    return {
        'tilt_correction': tilt_correction,
        'tilt_transform': tilt_transform.to_dict(),
        'tilt_swc_key': morphology_to_s3(
            bucket, f"{prefix}/tilt_morphology.swc", tilted_morphology)
    }


def run_tilt(token=None):
    reconstruction_id = os.environ["RECONSTRUCTION_ID"]
    working_bucket = os.environ["WORKING_BUCKET"]
    run_prefix = os.environ["RUN_PREFIX"]
    upright_swc_key = os.environ["UPRIGHT_SWC_KEY"]

    args = collect_inputs(working_bucket,
                          run_prefix,
                          reconstruction_id,
                          upright_swc_key)
    (tilt_correction, tilt_transform) = run_tilt_correction(**args)

    tf_morph = tilt_transform.transform_morphology(args['morphology'])

    return put_outputs(working_bucket, run_prefix,
                       tilt_correction, tilt_transform, tf_morph)


def main():
    step_fns_ecs_harness(run_tilt)


if __name__ == "__main__":
    main()
