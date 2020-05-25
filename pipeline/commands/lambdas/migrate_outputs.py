import traceback

import boto3


s3 = boto3.Client("s3")


def handler(event, context):
    try:
        print(event)

    except Exception as err:
        print(err)
        traceback.print_exc()
        raise