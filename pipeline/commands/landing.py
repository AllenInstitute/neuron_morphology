import os
import zipfile
import json
import io
import uuid
from datetime import datetime
from typing import Optional

import boto3

from harness import step_fns_ecs_harness


s3 = boto3.client("s3")


def extract_reconstruction_id(key: str):
    """The reconstruction id is the name of the upload package
    """
    return key.split("/")[-1].split(".")[0]


def get_raw_swc_key(
        working_bucket: str, 
        base_key: str, 
        reconstruction_id: str
) -> str:
    """Obtain the working bucket key of the raw SWC
    """

    input_json_key = f"{base_key}/{reconstruction_id}.json"
    input_json_response = s3.get_object(
        Bucket=working_bucket, Key=input_json_key
    )
    input_data = json.load(input_json_response["Body"])
    return f"{base_key}/{input_data['swc_file']}"


def landing(token: Optional[str] = None):
    """Extract a zip archive of pipeline inputs from the landing bucket and 
    transfer them to the working bucket. Generate an id for this run.

    Returns
    -------
    a dictionary:
        base_key : The prefix of the unzipped object keys in the working bucket
        bucket_name : the working bucket's name
        reconstruction_id : The identifier of this reconstruction
        run_id : A generated identifier for this pipeline run
        run_tilt: bool to run tilt step or not
        now: the date and time at which this task started

    """
    working_bucket = os.environ["WORKING_BUCKET"]
    landing_bucket = os.environ["LANDING_BUCKET"]
    upload_package_key = os.environ["UPLOAD_PACKAGE_KEY"]

    run_id = str(uuid.uuid4())
    reconstruction_id = extract_reconstruction_id(upload_package_key)
    now = datetime.now().strftime(r"%Y-%m-%d-%H-%M-%S")
    base_key = f"{reconstruction_id}/{now}_{run_id}"

    upload_package_response = s3.get_object(
        Bucket=landing_bucket, Key=upload_package_key
    )

    archive = zipfile.ZipFile(
        io.BytesIO(
            upload_package_response["Body"].read()
        )
    )
    zipped_metadata = archive.read(f"{reconstruction_id}.json")
    metadata = json.loads(zipped_metadata.decode("utf-8"))

    for name in archive.namelist():
        s3.put_object(
            Body=archive.read(name),
            Bucket=working_bucket,
            Key=f"{base_key}/{name}"
        )

    return {
        "base_key": base_key,
        "bucket_name": working_bucket,
        "reconstruction_id": reconstruction_id,
        "run_id": run_id,
        "run_tilt": (metadata['slice_transform'] is not None),
        "now": now,
        "raw_swc_key": get_raw_swc_key(
            working_bucket, base_key, reconstruction_id
        )
    }


def main():
    step_fns_ecs_harness(landing)


if __name__ == "__main__":
    main()
