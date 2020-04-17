import os
import boto3
import logging

def post_file_to_s3(file_name, bucket_name):
    """
    This is to post data to S3 bucket
    
    Parameters
    ------------------
    file_name: the file need to be uploaded
    bucket_name: s3 bucket name
    
    Return
    ------------------
    
    """
    aws_id = os.getenv('aws_access_key_id')
    aws_key = os.getenv('aws_secret_access_key')
    
    s3_client = boto3.client(
        's3',
        aws_access_key_id= aws_id,
        aws_secret_access_key= aws_key
    )
    
    response = s3_client.upload_file(file_name, bucket_name, file_name)
    
    
