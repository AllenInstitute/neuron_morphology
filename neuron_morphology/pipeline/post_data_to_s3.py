import os
import boto3
import logging
from botocore.exceptions import ClientError
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO


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
    file_list: file paths to be archived

    Return
    ---------------
    archive: BytesIO obj

    """

    archive = BytesIO()

    with ZipFile(archive, "a", ZIP_DEFLATED, False) as zip_file:
        for file_path in file_list:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as fh:
                data = BytesIO(fh.read())

            zip_file.writestr(file_name, data.getvalue())

    return archive


def post_files_to_s3(archive_name, file_list, bucket_name):
    """
    This zip files to an archive in memory and post it to S3 bucket

    Parameters
    ------------------
    archive_name: the archive's name in s3
    file_list: files' paths to be archived
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