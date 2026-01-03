"""
SendGrid HTTP API email backend
Uses HTTP instead of SMTP to avoid port blocking on cloud platforms
"""
from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Content
import logging

logger = logging.getLogger(__name__)


class SendGridBackend(BaseEmailBackend):
    """
    Email backend that uses SendGrid HTTP API instead of SMTP
    Works on Railway/Heroku where SMTP ports are blocked
    """
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent
        """
        if not email_messages:
            return 0
        
        from django.conf import settings
        api_key = settings.SENDGRID_API_KEY
        
        if not api_key: 
            logger.error("SENDGRID_API_KEY is not configured")
            if not self.fail_silently:
                raise ValueError("SENDGRID_API_KEY is required for SendGrid backend")
            return 0
        
        sg = SendGridAPIClient(api_key)
        num_sent = 0
        
        for message in email_messages:
            try:
                # Determine content type
                if message.content_subtype == 'html':
                    content = Content("text/html", message.body)
                else:
                    content = Content("text/plain", message.body)
                
                # Build SendGrid email
                mail = Mail(
                    from_email=message.from_email,
                    to_emails=message.to,
                    subject=message.subject,
                    plain_text_content=content if message.content_subtype != 'html' else None,
                    html_content=content if message.content_subtype == 'html' else None
                )
                
                # Send via HTTP API
                response = sg.send(mail)
                
                if response.status_code in [200, 201, 202]:
                    num_sent += 1
                    logger.info(f"Email sent successfully to {message.to} (status: {response.status_code})")
                else:
                    logger.error(f"Email failed with status {response.status_code}")
                    if not self.fail_silently:
                        raise Exception(f"SendGrid returned status {response.status_code}")
                        
            except Exception as e: 
                logger.error(f"Failed to send email: {e}")
                if not self.fail_silently:
                    raise
        
        return num_sent