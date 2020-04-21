import pytest
import os
import boto3
import zipfile
from moto import mock_s3

from neuron_morphology.pipeline.post_data_to_s3 import post_files_to_s3

path_to_current_file = os.path.realpath(__file__)
current_directory = os.path.split(path_to_current_file)[0]

file_name1 = "test_post_data_to_s3.py"
file_name2 = "__init__.py"

file_path1 = os.path.join(current_directory, file_name1)
file_path2 = os.path.join(current_directory, file_name2)

file_list = {file_name1: file_path1, file_name2: file_path2}
bucket_name = "neuronmorphologypipeline"
archive_name = "test_post_data.zip"

@mock_s3
def test_post_data_to_s3(tmpdir_factory):
    
    temp_output_dir = str(tmpdir_factory.mktemp("test"))
    temp_output_file = os.path.join(temp_output_dir, archive_name)

    s3 = boto3.resource('s3')
    s3.create_bucket(Bucket=bucket_name)

    post_files_to_s3(archive_name, file_list, bucket_name)
        
    s3_client = boto3.client(
                    's3',
                    aws_access_key_id=os.getenv('aws_access_key_id'),
                    aws_secret_access_key=os.getenv('aws_secret_access_key')
                )

    s3_client.download_file(bucket_name, archive_name, temp_output_file)

    archive = zipfile.ZipFile(temp_output_file, 'r')

    assert all([a.filename == b for a, b in zip(archive.infolist(), [file_name1, file_name2])])
