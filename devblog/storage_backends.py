"""
Custom S3 storage backend for media files
Bucket policy handles public access, not ACLs
"""
from storages.backends.s3boto3 import S3Boto3Storage


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for user-uploaded media files"""
    location = 'media'
    file_overwrite = False
    
    # Don't set ACL - bucket policy handles public access
    default_acl = None
    querystring_auth = False