import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devblog.settings')
django.setup()

from django.contrib.sites.models import Site

# Fix Site configuration
try:
    site = Site.objects.get(id=1)
    site.domain = 'web-production-5b3220.up.railway.app'
    site.name = 'DevBlog'
    site.save()
    print(f'✅ Site updated: {site.domain}')
except Site.DoesNotExist:
    site = Site.objects.create(
        id=1,
        domain='web-production-5b3220.up. railway.app',
        name='DevBlog'
    )
    print(f'✅ Site created: {site.domain}')

print('🎉 Site configuration complete!')