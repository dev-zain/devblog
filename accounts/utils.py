from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from django.core.mail import EmailMessage
from . tokens import account_activation_token
import logging

logger = logging.getLogger(__name__)


def send_activation_email(request, user):
    """Send activation email to user"""
    try:
        current_site = get_current_site(request)
        subject = 'Activate your DevBlog account'
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"http://{current_site.domain}/accounts/activate/{uid}/{token}/"
        
        # Get display name (full name if available, otherwise username)
        display_name = user.get_full_name() or user.username
        
        # Render email template
        html_message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'display_name': display_name,
            'domain': current_site.domain,
            'uid': uid,
            'token': token,
            'activation_link': activation_link,
        })
        
        # Create plain text version
        plain_message = f"""
Hi {display_name},

Thank you for registering at DevBlog!

Please click the link below to activate your account:
{activation_link}

This link will expire in 7 days.

If you didn't create an account, please ignore this email.

Thanks,
The DevBlog Team
"""
        
        # Send email using EmailMessage for better control
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email],
        )
        email.content_subtype = 'html'  # Set content type to HTML
        email.send(fail_silently=False)
        
        logger.info(f"Activation email sent successfully to {user.email}")
        
    except Exception as e:
        logger.error(f"Failed to send activation email to {user.email}: {str(e)}")
        raise  # Re-raise to show error to user