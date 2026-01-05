"""
Custom S3 storage backend for media files only
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """
    S3 storage backend for user-uploaded media files (images, etc.)
    """
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False