import os
import traceback

import boto3


step_fns = boto3.client("stepfunctions")


def main():
    
    token = os.environ.get("TASK_TOKEN")
    
    try:

        working_bucket = os.environ.get("WORKING_BUCKET")
        landing_bucket = os.environ.get("LANDING_BUCKET")
        upload_package_key = os.environ.get("UPLOAD_PACKAGE_KEY")

        output = {"foo": "bar"}

    except Exception as err:
        print(err)
        traceback.print_exc()
        step_fns.send_task_failure(
            taskToken=token,
            error: str(err),
            cause: traceback.format_exc()
        )
        raise

    step_fns.send_task_success(
        token,

    )


if __name__ == "__main__":
    main()