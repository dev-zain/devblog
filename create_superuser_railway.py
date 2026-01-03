import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devblog.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin'
email = 'admin@devblog.com'
password = 'YourPassword123!'  # Change this! 

# Delete if exists and recreate
if User.objects.filter(username=username).exists():
    User.objects.filter(username=username).delete()
    print(f'🗑️  Deleted existing user:  {username}')

user = User.objects.create_superuser(username=username, email=email, password=password)
print(f'✅ Superuser created on Railway database!')
print(f'   Username:  {username}')
print(f'   Password: {password}')
print(f'   Email: {email}')