from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from . tokens import account_activation_token


def send_activation_email(request, user):
    """Send activation email to user"""
    current_site = get_current_site(request)
    subject = 'Activate your DevBlog account'
    
    message = render_to_string('accounts/activation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user. pk)),
        'token': account_activation_token.make_token(user),
    })
    
    send_mail(
        subject,
        message,
        'noreply@devblog. com',
        [user.email],
        fail_silently=False,
    )