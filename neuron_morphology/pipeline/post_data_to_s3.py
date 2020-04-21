import os
import boto3
import logging
import json
from botocore.exceptions import ClientError
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from argschema import ArgSchemaParser
from neuron_morphology.pipeline._schemas import InputParameters

def post_file_to_s3(file_name, bucket_name):
    """
    This is to post data to S3 bucket
    
    Parameters
    ------------------
    file_name: the file need to be uploaded
    bucket_name: s3 bucket name
    
    Return
    ------------------
    True if successful

    """
    aws_id = os.getenv('aws_access_key_id')
    aws_key = os.getenv('aws_secret_access_key')
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id= aws_id,
            aws_secret_access_key= aws_key
        )

        response = s3_client.upload_file(file_name, bucket_name, file_name)

    except ClientError as e:
        logging.error(e)
        return False
    return True


def zip_files(file_list):
    """
    zip files into an archive in memory

    Parameters
    ---------------
    file_list: file paths or file in bytes to be archived

    Return
    ---------------
    archive: BytesIO obj

    """

    archive = BytesIO()

    with ZipFile(archive, "a", ZIP_DEFLATED, False) as zip_file:
        for name, file in file_list.items():
            if isinstance(file, str):
                with open(file, 'rb') as fh:
                    data = BytesIO(fh.read())
                zip_file.writestr(name, data.getvalue())
            elif isinstance(file, BytesIO):
                zip_file.writestr(name, file.getvalue())
            else:
                raise TypeError("Invalid input file!")

    return archive


def post_files_to_s3(archive_name, file_list, bucket_name):
    """
    This zip files to an archive in memory and post it to S3 bucket

    Parameters
    ------------------
    archive_name: the archive's name in s3
    file_list: file paths or files in bytes to be archived
    bucket_name: s3 bucket name
    
    Return
    ------------------
    True if successful
    
    """

    archive = zip_files(file_list)

    aws_id = os.getenv('aws_access_key_id')
    aws_key = os.getenv('aws_secret_access_key')
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id= aws_id,
            aws_secret_access_key= aws_key
        )

        response = s3_client.put_object(Bucket=bucket_name, 
                                    Key=archive_name, 
                                    Body=archive.getvalue())

    except ClientError as e:
        logging.error(e)
        return False
    return True


def main():
    """
    Usage:
    python post_data_to_s3.py --input_json INPUT_JSON
    """
    parser = ArgSchemaParser(schema_type=InputParameters)
    inputs = parser.args

    file_list = {}

    if inputs['swc_file'] is not None:
        swc_file_name = os.path.basename(inputs['swc_file'])
        file_list[swc_file_name] = inputs['swc_file']
        inputs['swc_file'] = swc_file_name

    if inputs['marker_file'] is not None:
        marker_file_name = os.path.basename(inputs['marker_file'])
        file_list[marker_file_name] = inputs['marker_file']
        inputs['marker_file'] = marker_file_name

    jsonData = json.dumps(inputs)
    binaryData = jsonData.encode()
    input_json = BytesIO(binaryData)

    json_fn = str(inputs['specimen_id']) + ".json"
    file_list[json_fn] = input_json

    archive_name = str(inputs['specimen_id']) + ".zip"
    bucket_name = inputs['s3_bucket_uri']

    post_files_to_s3(archive_name, file_list, bucket_name)


if __name__ == "__main__":
    main()