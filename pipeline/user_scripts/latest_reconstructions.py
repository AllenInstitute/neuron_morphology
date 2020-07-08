import argparse
import os

import boto3
import pandas as pd

dynamo = boto3.client("dynamodb")
s3 = boto3.client("s3")


def scan_all(*args, **kwargs):
    """Scan all rows of a dynamo table
    """
    last_key = "tmp"
    results = []
    while last_key:
        last_key = {}
        if last_key:
            kwargs.update({"ExclusiveStartKey": last_key})
        response = dynamo.scan(*args, **kwargs)
        results.extend(response["Items"])
        last_key = response.get("LastEvaluatedKey", {})
    return results


def main():
    parser = argparse.ArgumentParser(
        description="downloads the latest final (transformed) swc "
                    "for each reconstruction")
    parser.add_argument(
        "runs_table_name",
        type=str,
        help="name of the dynamodb table listing all successful pipeline runs")
    parser.add_argument(
        "results_path",
        type=str,
        help="results will be written into this directory")
    parser.add_argument(
        '--reconstruction_ids',
        nargs='+',
        type=int,
        help='list of reconstruction ids to retrieve')
    args = parser.parse_args()

    runs = []
    for item in scan_all(TableName=args.runs_table_name):
        runs.append({key: item[key]["S"] for key in item})
    runs = pd.DataFrame(runs)

    if args.reconstruction_ids:
        runs = runs.loc[runs['ReconstructionId'].isin(
            [str(rid) for rid in args.reconstruction_ids])]

    os.makedirs(args.results_path, exist_ok=True)
    for (recon_id, recon) in runs.groupby("ReconstructionId"):
        recon = pd.DataFrame(recon).sort_values(by="LandingTime")
        print(f"recon: {recon_id}, run: {recon['RunId'].values[-1]}")
        s3.download_file(
            Bucket=recon["DataBucket"].values[-1],
            Key=recon["FinalSwcKey"].values[-1],
            Filename=os.path.join(args.results_path,
                                  f"{recon_id}_transformed.swc")
        )
        s3.download_file(
            Bucket=recon["DataBucket"].values[-1],
            Key=recon["RawSwcKey"].values[-1],
            Filename=os.path.join(args.results_path,
                                  f"{recon_id}_raw.swc")
        )
        # marker file is same name as raw except with .marker extension
        s3.download_file(
            Bucket=recon["DataBucket"].values[-1],
            Key=recon["RawSwcKey"].values[-1][:-3]+'marker',
            Filename=os.path.join(args.results_path,
                                  f"{recon_id}.marker")
        )

    runs.to_csv(os.path.join(args.results_path, "runs.csv"))


if __name__ == "__main__":
    main()
