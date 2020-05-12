import io
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
        url = urlparse(url)
        assert url.scheme == 's3'
        self.s3 = boto3.client('s3')
        self.bucket_name = url.hostname
        self.object_key = url.path[1:]

    def get_size(self):
        try:
            head = self.s3.head_object(
                Bucket=self.bucket_name,
                Key=self.object_key)
            return int(head['ContentLength'])
        except ClientError:
            return 0

    def delete(self):
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
        with file.stream() as file:
            self.s3.upload_fileobj(
                file,
                Bucket=self.bucket_name,
                Key=self.object_key)

    def stream(self):
        return self.s3.get_object(
            Bucket=self.bucket_name,
            Key=self.object_key)['Body']._raw_stream
