from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings

class MediaStorage(S3Boto3Storage):
    location = "media"
    file_overwrite = False
    default_acl = None
    querystring_auth = False
    custom_domain = settings.AWS_S3_CUSTOM_DOMAIN