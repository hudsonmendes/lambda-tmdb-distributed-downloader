from typing import Dict
import io
import json
import boto3
import tempfile
from botocore.exceptions import ClientError
from urllib.parse import urlparse

from .file_http import FileHttp


class FileS3:
    """
    Wrapper for S3 File, providing access to the DataLake,
    size checking, streaming and writing
    """

    def __init__(self, url: str, **kwargs):
        self.url = url
        url = urlparse(url)
        assert url.scheme == 's3'
        self.s3 = boto3.client('s3')
        self.bucket_name = url.hostname
        self.object_key = url.path[1:]

    def get_size(self) -> int:
        """
        Attempts to get the size of the file in bytes from S3.
        If it fails, or if it does not find the file, returns 0.
        """
        try:
            head = self.s3.head_object(
                Bucket=self.bucket_name,
                Key=self.object_key)
            return int(head['ContentLength'])
        except ClientError:
            return 0

    def delete(self):
        """
        Deletes the file from S3
        """ 
        self.s3.delete_object(
            Bucket=self.bucket_name,
            Key=self.object_key)

    def touch(self):
        with tempfile.NamedTemporaryFile() as file:
            file.write('touchè'.encode('utf-8'))
            file.flush()
            file.seek(0)
            self.s3.upload_fileobj(
                file,
                Bucket=self.bucket_name,
                Key=self.object_key)

    def copy_from(self, file: FileHttp):
        """
        Copies from a HTTP file into an S3 object.
        Does not download/upload the file. It streams
        the file directly instead.
        """
        with file.stream() as file:
            self.s3.upload_fileobj(
                file,
                Bucket=self.bucket_name,
                Key=self.object_key)

    def write(self, json_data: Dict):
        """
        Writes data into JSON format.
        """
        with tempfile.TemporaryFile() as temp_file:
            temp_file.write(json.dumps(json_data).encode('utf-8'))
            temp_file.seek(0)
            self.s3.upload_fileobj(
                temp_file,
                Bucket=self.bucket_name,
                Key=self.object_key)

    def stream(self):
        """
        Gets the file stream from S3, without downloading
        the file locally.
        """
        return self.s3.get_object(
            Bucket=self.bucket_name,
            Key=self.object_key)['Body']._raw_stream
