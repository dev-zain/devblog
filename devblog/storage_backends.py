"""
Custom S3 storage backend for media files
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for user-uploaded media files"""
    location = 'media'
    default_acl = None  # Bucket policy handles public access
    file_overwrite = False
    querystring_auth = False