import os
import boto3
import json
import configparser
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from argschema import ArgSchemaParser
from neuron_morphology.pipeline._schemas import InputParameters

def get_credentials(credentials_file):
    """
    get credentisals from credentials_file

    Parameters
    ---------------
    credentials_file: file path to credentials_file

    Return
    ---------------
    credentials: access_key_id, secret_access_key

    """
    config = configparser.ConfigParser()
    config.read(credentials_file)
    access_key_id = None
    secret_access_key = None
    if 'default' in config.sections():
        if 'aws_access_key_id' in config.options('default'):
            access_key_id = config.get('default', 'aws_access_key_id')
        if 'aws_access_key_id' in config.options('default'):
            secret_access_key = config.get('default', 'aws_secret_access_key')

    return access_key_id, secret_access_key

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


def post_object_to_s3(data, name, bucket, region, access_key_id=None, secret_access_key=None):
    """
    post object (bytes) in memory to S3 bucket

    Parameters
    ------------------
    data: the object data
    name: the object data's name in s3
    region: where the s3 bucket located
    bucket: s3 bucket name or arn
    access_key_id, secret_access_key: aws user's credentials
        implicitly the credentials file located in ~/.aws/credentials or
        set AWS_SHARED_CREDENTIALS_FILE to the credentials file in your environment
    
    Return
    ------------------
    True if successful
    
    """
    if access_key_id and secret_access_key:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region
        )
    else:
        s3_client = boto3.client('s3', region_name=region)

    response = s3_client.put_object(Bucket=bucket, 
                                Key=name, 
                                Body=data)


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

    json_data = json.dumps(inputs)
    binary_data = json_data.encode()
    input_json = BytesIO(binary_data)

    json_fn = str(inputs['neuron_reconstruction_id']) + ".json"
    file_dict[json_fn] = input_json

    archive_data = zip_files(file_dict)
    archive_name = str(inputs['neuron_reconstruction_id']) + ".zip"
    bucket = inputs['destination_bucket']['name']
    bucket_region = inputs['destination_bucket']['region']
    credentials_file = inputs['destination_bucket']['credentials_file']
    access_key_id, secret_access_key = get_credentials(credentials_file)

    post_object_to_s3(archive_data.getvalue(), archive_name, bucket, bucket_region, access_key_id, secret_access_key)


if __name__ == "__main__":
    main()