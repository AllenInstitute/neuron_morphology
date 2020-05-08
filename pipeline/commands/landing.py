import os
import traceback
import json
import zipfile
import io
import uuid

import boto3


step_fns = boto3.client("stepfunctions")
s3 = boto3.client("s3")


def extract_reconstruction_id(key):
    return key.split("/")[-1].split(".")[0]


def main():
    
    token = os.environ["TASK_TOKEN"]
    
    try:

        working_bucket = os.environ["WORKING_BUCKET"]
        landing_bucket = os.environ["LANDING_BUCKET"]
        upload_package_key = os.environ["UPLOAD_PACKAGE_KEY"]

        run_id = uuid.uuid4()
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
                Key=f"{base_key}/{name}"
            )

        s3.delete_object(Bucket=landing_bucket, Key=upload_package_key)

        output = {
            "base_key": base_key,
            "bucket_name": working_bucket
        }

    except Exception as err:
        print(err)
        traceback.print_exc()
        step_fns.send_task_failure(
            taskToken=token,
            error=str(err),
            cause=traceback.format_exc()
        )
        raise

    step_fns.send_task_success(
        taskToken=token,
        output=json.dumps(output)
    )


if __name__ == "__main__":
    main()
