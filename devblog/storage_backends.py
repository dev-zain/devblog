"""
Custom S3 storage backend for media files with detailed logging
"""
from storages.backends.s3boto3 import S3Boto3Storage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for user-uploaded media files"""
    location = 'media'
    default_acl = None
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        logger.info(f"📦 S3 Storage initialized")
        logger.info(f"🪣 Bucket: {settings.AWS_STORAGE_BUCKET_NAME}")
        logger.info(f"🌍 Region: {settings.AWS_S3_REGION_NAME}")
        logger.info(f"🔑 Access Key: {settings.AWS_ACCESS_KEY_ID[: 10]}...")
        logger.info(f"🔐 Secret Key: {'SET' if settings.AWS_SECRET_ACCESS_KEY else 'NOT SET'}")
    
    def _save(self, name, content):
        logger.info(f"🚀 Attempting S3 upload: {name}")
        logger.info(f"📂 Full S3 path: {self.location}/{name}")
        try:
            result = super()._save(name, content)
            logger.info(f"✅ SUCCESS!  File uploaded to S3: {result}")
            full_url = self.url(result)
            logger.info(f"🌐 File URL: {full_url}")
            return result
        except Exception as e:
            logger.error(f"❌ S3 UPLOAD FAILED!")
            logger.error(f"❌ Error type: {type(e).__name__}")
            logger.error(f"❌ Error message: {str(e)}")
            import traceback
            logger.error(f"❌ Full traceback:\n{traceback.format_exc()}")
            raise