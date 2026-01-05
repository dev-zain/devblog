"""
Custom S3 storage backends for static and media files
"""
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """S3 storage backend for static files"""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for media files (user uploads)"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False 