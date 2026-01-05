"""
Custom S3 storage backend for media files
"""
from storages.backends.s3boto3 import S3Boto3Storage
import logging
import sys

# Force logging to stderr
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stderr)
handler.setLevel(logging.INFO)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

print("🔥 storage_backends.py MODULE LOADED!", file=sys.stderr)


class MediaStorage(S3Boto3Storage):
    """S3 storage backend for user-uploaded media files"""
    location = 'media'
    default_acl = None
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        print("🔥 MediaStorage.__init__() called!", file=sys.stderr)
        super().__init__(*args, **kwargs)
        print(f"✅ MediaStorage initialized for bucket: {self.bucket_name}", file=sys.stderr)
    
    def _save(self, name, content):
        print(f"🔥 MediaStorage._save() called!  File: {name}", file=sys.stderr)
        print(f"📂 Full path will be: {self.location}/{name}", file=sys.stderr)
        
        try:
            result = super()._save(name, content)
            print(f"✅ Upload SUCCESS! Result: {result}", file=sys.stderr)
            url = self.url(result)
            print(f"🌐 File URL: {url}", file=sys.stderr)
            return result
        except Exception as e:
            print(f"❌ Upload FAILED! Error: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            raise


print("🔥 storage_backends.py: MediaStorage class defined!", file=sys.stderr)