import traceback
import os
from typing import Dict

import boto3


s3 = boto3.client("s3")
dynamo = boto3.client("dynamodb")


class Outputter:

    def __init__(self, event: Dict, environ: Dict):
        """Responsible for moving outputs to persistent storage and updating 
        databases.
        """

        self.working_bucket = event["landing"]["bucket_name"]
        self.run_id = event["landing"]["run_id"]
        self.recon_id = event["landing"]["reconstruction_id"]
        self.has_tilt = event["landing"]["run_tilt"]
        self.prefix = event["landing"]["base_key"]
        self.landing_time = event["landing"]["now"]

        self.output_bucket = environ["OUTPUT_BUCKET"]
        self.runs_table = environ["RUNS_TABLE"]
        self.recons_table = environ["RECONSTRUCTIONS_TABLE"]

        if self.has_tilt:
            self.final_swc_key = event["tilt"]["tilt_swc_key"]
        else:
            self.final_swc_key = event["upright_transform"]["upright_swc_key"]

    def copy_working_objects(self):
        """Copy all of the data input to and produced by this run to the output 
        bucket
        """
        response = s3.list_objects_v2(
            Bucket=self.working_bucket, Prefix=self.prefix
        )

        for item in response["Contents"]:
            s3.copy_object(
                Bucket=self.output_bucket, Key=item["Key"],
                CopySource={"Bucket": self.working_bucket, "Key": item["Key"]}
            )

        return self

    def update_runs_table(self):
        """Add a new item to the runs table, describing this run of the 
        pipeline
        """
        dynamo.put_item(
            TableName=self.runs_table,
            Item={
                "RunId": {"S": self.run_id},
                "ReconstructionId": {"S": str(self.recon_id)},
                "LandingTime": {"S": self.landing_time},
                "DataBucket": {"S": self.output_bucket},
                "Prefix": {"S": self.prefix},
                "FinalSwcKey": {"S": self.final_swc_key}
            }
        )
        return self

    def update_reconstructions_table(self):
        """Update the record for this run's reconstruction inplace to 
        """
        dynamo.put_item(
            TableName=self.recons_table,
            Item={
                "ReconstructionId": {"S": str(self.recon_id)},
                "LatestRunId": {"S": str(self.run_id)}
            }
        )
        return self


def handler(event, context):
    try:
        print(event)

        (
            Outputter(event, os.environ)
            .copy_working_objects()
            .update_runs_table()
            .update_reconstructions_table()
        )

    except Exception as err:
        print(err)
        traceback.print_exc()
        raise
