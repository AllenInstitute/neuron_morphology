import os
import traceback
import json
from typing import Callable, Optional, Dict

import boto3


step_fns = boto3.client("stepfunctions")


def step_fns_ecs_harness(
        callback: Callable[[Optional[str]], Dict]
):
    """Utilty for running a python function and reporting results back via 
    AWS task token interface.

    Parameters
    ----------
    callback : The function to run. Must accept a "token" kwarg, but doesn't 
        need to use it (could be used to send heartbeats, for instance). This 
        function is responsible for collecting its inputs from the environment.
    """

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