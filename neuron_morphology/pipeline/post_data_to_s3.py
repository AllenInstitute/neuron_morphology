import os
import boto3
import json
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from argschema import ArgSchemaParser
from neuron_morphology.pipeline._schemas import InputParameters

def zip_files(file_dict):
    """
    zip files into an archive in memory

    Parameters
    ---------------
    file_dict: file name: file paths or file in bytes to be archived

    Return
    ---------------
    archive: BytesIO obj

    """

    archive = BytesIO()

    with ZipFile(archive, "a", ZIP_DEFLATED, False) as zip_file:
        for name, file in file_dict.items():
            if isinstance(file, str):
                with open(file, 'rb') as fh:
                    data = BytesIO(fh.read())
                zip_file.writestr(name, data.getvalue())
            elif isinstance(file, BytesIO):
                zip_file.writestr(name, file.getvalue())
            else:
                raise TypeError("Invalid input file!")

    return archive


def post_object_to_s3(archive_data, archive_name, bucket, region):
    """
    This zip files to an archive in memory and post it to S3 bucket

    Parameters
    ------------------
    archive_data: the archive data
    archive_name: the archive's name in s3
    region: where the s3 bucket located
    bucket: s3 bucket name or arn
    
    Return
    ------------------
    True if successful
    
    """

    aws_id = os.getenv('aws_access_key_id')
    aws_key = os.getenv('aws_secret_access_key')
    
    s3_client = boto3.client('s3', region_name=region)

    response = s3_client.put_object(Bucket=bucket, 
                                Key=archive_name, 
                                Body=archive_data.getvalue())


def main():
    """
    Usage:
    python post_data_to_s3.py --input_json INPUT_JSON
    """
    parser = ArgSchemaParser(schema_type=InputParameters)
    inputs = parser.args

    file_dict = {}

    swc_file_name = os.path.basename(inputs['swc_file'])
    file_dict[swc_file_name] = inputs['swc_file']
    inputs['swc_file'] = swc_file_name

    if inputs['marker_file'] is not None:
        marker_file_name = os.path.basename(inputs['marker_file'])
        file_dict[marker_file_name] = inputs['marker_file']
        inputs['marker_file'] = marker_file_name

    jsonData = json.dumps(inputs)
    binaryData = jsonData.encode()
    input_json = BytesIO(binaryData)

    json_fn = str(inputs['neuron_reconstruction_id']) + ".json"
    file_dict[json_fn] = input_json

    archive_data = zip_files(file_dict)
    archive_name = str(inputs['neuron_reconstruction_id']) + ".zip"
    bucket_name = inputs['s3_bucket']
    region = inputs['s3_bucket_region']

    post_object_to_s3(archive_data, archive_name, bucket_name, region)


if __name__ == "__main__":
    main()