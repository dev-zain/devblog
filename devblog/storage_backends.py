"""
Custom S3 storage backend for media files
"""
from storages.backends.s3boto3 import S3Boto3Storage
import logging

logger = logging.getLogger(__name__)


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for user-uploaded media files"""
    location = 'media'
    default_acl = None
    file_overwrite = False
    querystring_auth = False
    
    def _save(self, name, content):
        logger.info(f"🚀 Attempting to save file to S3: {name}")
        logger.info(f"📦 Bucket: {self.bucket_name}")
        logger.info(f"🌍 Region: {self.region_name}")
        try:
            result = super()._save(name, content)
            logger.info(f"✅ Successfully saved to S3: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ S3 upload failed: {str(e)}")
            raise