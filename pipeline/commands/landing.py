import os
import zipfile
import io
import uuid

import boto3

from harness import step_fns_ecs_harness


s3 = boto3.client("s3")


def extract_reconstruction_id(key):
    return key.split("/")[-1].split(".")[0]


def landing(token=None):
    working_bucket = os.environ["WORKING_BUCKET"]
    landing_bucket = os.environ["LANDING_BUCKET"]
    upload_package_key = os.environ["UPLOAD_PACKAGE_KEY"]

    run_id = str(uuid.uuid4())
    reconstruction_id = extract_reconstruction_id(upload_package_key)
    base_key = f"{reconstruction_id}/{run_id}"

    upload_package_response = s3.get_object(
        Bucket=landing_bucket, Key=upload_package_key
    )

    archive = zipfile.ZipFile(
        io.BytesIO(
            upload_package_response["Body"].read()
        )
    )

    for name in archive.namelist():
        s3.put_object(
            Body=archive.read(name),
            Bucket=working_bucket,
            Key=f"{base_key}/{name}"
        )

    s3.delete_object(Bucket=landing_bucket, Key=upload_package_key)

    return {
        "base_key": base_key,
        "bucket_name": working_bucket,
        "reconstruction_id": reconstruction_id,
        "run_id": run_id
    }


def main():
    step_fns_ecs_harness(landing)


if __name__ == "__main__":
    main()
