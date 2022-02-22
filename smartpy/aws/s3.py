from urllib.parse import urlparse
import json
import pickle
import tempfile

import boto3
from s3fs.core import S3FileSystem


class S3:

    def __init__(self, profile_name=None, **kwargs):
        # We need this so setup the proper session locally
        # boto3.setup_default_session(profile_name=profile_name)
        my_session = boto3.session.Session(profile_name=profile_name)

        self.boto3_client = my_session.client('s3',
                                         **kwargs)
        self.boto3_resource = my_session.resource('s3',
                                             **kwargs)
        self.s3fs = S3FileSystem(session=my_session)

    # Pulling
    def downloadFile(self, bucket, key, save_to_path):
        if self.checkIfObjectExists(bucket, key):
            print(f'Downloading to {save_to_path}')
            self.boto3_resource.Bucket(bucket).download_file(key, save_to_path)
        else:
            raise Exception(f"The key {key} doesn't exist")

    def getTempfile(self, bucket, key):
        f = tempfile.NamedTemporaryFile()
        self.boto3_resource.Bucket(bucket).download_file(key, f.name)
        return f

    def getJson(self, bucket, key):
        obj = self.boto3_client.get_object(Bucket=bucket, Key=key)
        content = obj['Body']
        jsonObject = json.loads(content.read())
        return jsonObject

    def getPickleFile(self, bucket, key):
        return pickle.load(self.s3fs.open('{}/{}'.format(bucket, key)))

    # Pushing
    def uploadFile(self, bucket, key, file_path):
        return self.boto3_resource.Bucket(bucket).upload_file(file_path, key)

    def uploadDictAsJson(self, bucket, key, dictionary):
        return self.boto3_client.put_object(Body=str(json.dumps(dictionary)), Bucket=bucket, Key=key)

    def deleteFile(self, bucket, key):
        return self.boto3_client.delete_object(Bucket=bucket, Key=key)

    # Utility
    def checkIfObjectExists(self, bucket, key):

        bucket = self.boto3_resource.Bucket(bucket)
        for object_summary in bucket.objects.filter(Prefix=key):
            return True
        return False

    def getObjectURI(self, bucket, key):
        return f"s3://{bucket}/{key}"

    def listFiles(self, bucket, key):
        """List files in specific S3 URL"""
        bucket = self.boto3_resource.Bucket(bucket)
        files_in_bucket = list(bucket.objects.all())
        return files_in_bucket

    def getBucketKeyFromUri(self, uri):
        parsed_uri = urlparse(uri, allow_fragments=False)
        return parsed_uri.netloc, parsed_uri.path[1:]