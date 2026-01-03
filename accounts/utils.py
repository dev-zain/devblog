from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.sites.shortcuts import get_current_site
from django.conf import settings
from . tokens import account_activation_token
import logging

logger = logging.getLogger(__name__)


def send_activation_email(request, user):
    """Send activation email to user"""
    try: 
        current_site = get_current_site(request)
        subject = 'Activate Your DevBlog Account'  # Clear, not spammy subject
        
        # Generate activation link
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = account_activation_token.make_token(user)
        activation_link = f"https://{current_site.domain}/accounts/activate/{uid}/{token}/"
        
        # Get display name
        display_name = user.get_full_name() or user.username
        
        # Render email template
        html_message = render_to_string('accounts/activation_email.html', {
            'user': user,
            'display_name': display_name,
            'domain': current_site.domain,
            'uid': uid,
            'token':  token,
            'activation_link': activation_link,
        })
        
        # Plain text fallback
        plain_message = f"""
Hi {display_name},

Welcome to DevBlog! 

Please activate your account by clicking the link below:
{activation_link}

This link will expire in 7 days.

If you didn't create this account, please ignore this email.

Thanks,
The DevBlog Team
"""
        
        # Create email with professional from address
        email = EmailMessage(
            subject=subject,
            body=html_message,
            from_email=f'DevBlog <{settings.DEFAULT_FROM_EMAIL}>',  # Display name
            to=[user.email],
            reply_to=[settings.DEFAULT_FROM_EMAIL],
        )
        email.content_subtype = 'html'
        
        # Send email
        email.send(fail_silently=False)
        
        logger.info(f"Activation email sent successfully to {user.email}")
        
    except Exception as e: 
        logger.error(f"Failed to send activation email to {user.email}: {str(e)}")
        raise