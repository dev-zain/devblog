"""
Custom S3 storage backend for media files
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for user-uploaded media files"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = False
    custom_domain = False  # Use direct S3 URLs
    
    def __init__(self, *args, **kwargs):
        kwargs['bucket_name'] = settings.AWS_STORAGE_BUCKET_NAME
        kwargs['region_name'] = settings.AWS_S3_REGION_NAME
        kwargs['access_key'] = settings.AWS_ACCESS_KEY_ID
        kwargs['secret_key'] = settings.AWS_SECRET_ACCESS_KEY
        kwargs['default_acl'] = 'public-read'
        super().__init__(*args, **kwargs)