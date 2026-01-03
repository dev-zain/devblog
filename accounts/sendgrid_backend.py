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
                # Build the Mail object properly
                mail = Mail()
                mail.from_email = message.from_email
                mail.subject = message.subject
                
                # Handle multiple recipients
                if isinstance(message.to, list):
                    for recipient in message.to:
                        mail.add_to(recipient)
                else: 
                    mail.add_to(message.to)
                
                # Set content based on content type
                if hasattr(message, 'content_subtype') and message.content_subtype == 'html':
                    # HTML email
                    mail.add_content(Content("text/html", message.body))
                else:
                    # Plain text email
                    mail.add_content(Content("text/plain", message.body))
                
                # Add alternatives if present (for multipart emails)
                if hasattr(message, 'alternatives') and message.alternatives:
                    for alternative_content, mimetype in message.alternatives:
                        if mimetype == 'text/html':
                            mail.add_content(Content("text/html", alternative_content))
                
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
                logger.error(f"Failed to send email:  {e}")
                if not self.fail_silently:
                    raise
        
        return num_sent