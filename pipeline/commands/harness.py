import os
import traceback
import json

import boto3


step_fns = boto3.client("stepfunctions")


def step_fns_ecs_harness(callback):

    token = os.environ["TASK_TOKEN"]

    try:
        output = callback(token=token)

    except Exception as err:
        print(type(err))
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