import pytest
import os
import boto3
import zipfile
from moto import mock_s3
import unittest

from neuron_morphology.pipeline.post_data_to_s3 import post_object_to_s3, zip_files

path_to_current_file = os.path.realpath(__file__)
current_directory = os.path.split(path_to_current_file)[0]

file_name1 = "test_post_data_to_s3.py"
file_name2 = "__init__.py"

file_path1 = os.path.join(current_directory, file_name1)
file_path2 = os.path.join(current_directory, file_name2)

file_dict = {file_name1: file_path1, file_name2: file_path2}
bucket_name = "neuronmorphologypipeline"
archive_name = "test_post_data.zip"
region = "us-west-2"

class TestZipFiles(unittest.TestCase):
    def setUp(self):
        self.mock_listing = [file_name1, file_name2]
        self.file_dict = file_dict

    def test_zip_files(self):
        
        archive = zip_files(self.file_dict)

        if zipfile.is_zipfile(archive): 
            file_list = [file_name for file_name in zipfile.ZipFile(archive).namelist()]

        self.assertListEqual(self.mock_listing, file_list)

@mock_s3
def test_post_data_to_s3(tmpdir_factory):
    
    temp_output_dir = str(tmpdir_factory.mktemp("test"))
    temp_output_file = os.path.join(temp_output_dir, archive_name)

    s3 = boto3.resource('s3', region_name=region)
    s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': 'us-west-2'})

    archive_data = zip_files(file_dict)
    post_object_to_s3(archive_data.getvalue(), archive_name, bucket_name, region)
        
    s3_client = boto3.client('s3', region)

    s3_client.download_file(bucket_name, archive_name, temp_output_file)

    archive = zipfile.ZipFile(temp_output_file, 'r')

    assert all([a.filename == b for a, b in zip(archive.infolist(), [file_name1, file_name2])])
