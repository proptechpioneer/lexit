"""
SendGrid Email Backend for Django
This custom backend uses SendGrid's API instead of SMTP, which works better with cloud providers like Railway.
"""

from django.core.mail.backends.base import BaseEmailBackend
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class SendGridBackend(BaseEmailBackend):
    """
    A Django email backend that uses SendGrid's API instead of SMTP.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = getattr(settings, 'SENDGRID_API_KEY', None)
        self.client = None
        
        if self.api_key:
            self.client = SendGridAPIClient(api_key=self.api_key)
    
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        if not self.client:
            logger.error("SendGrid API key not configured")
            return 0
            
        sent_count = 0
        for message in email_messages:
            sent = self._send_message(message)
            if sent:
                sent_count += 1
        return sent_count
    
    def _send_message(self, email_message):
        """Send a single EmailMessage using SendGrid API"""
        try:
            print(f"DEBUG: Attempting to send email to {email_message.to}")
            print(f"DEBUG: From email: {email_message.from_email}")
            print(f"DEBUG: Subject: {email_message.subject}")
            print(f"DEBUG: API Key configured: {bool(self.api_key)}")
            
            # Create the SendGrid Mail object - fix for plain text content
            mail = Mail(
                from_email=email_message.from_email,
                to_emails=email_message.to[0] if email_message.to else email_message.to,  # SendGrid expects single email or list
                subject=email_message.subject,
                plain_text_content=email_message.body  # Always use plain text content
            )
            
            print(f"DEBUG: Mail object created successfully")
            
            # Send the email
            response = self.client.send(mail)
            print(f"DEBUG: SendGrid response status: {response.status_code}")
            print(f"DEBUG: SendGrid response body: {response.body}")
            
            # Check if successful (status code 202 indicates accepted)
            if response.status_code == 202:
                logger.info(f"Email sent successfully to {email_message.to}")
                print(f"DEBUG: Email sent successfully!")
                return True
            else:
                logger.error(f"SendGrid API error: {response.status_code}, Response: {response.body}")
                print(f"DEBUG: SendGrid error - Status: {response.status_code}, Body: {response.body}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {str(e)}")
            print(f"DEBUG: Exception in _send_message: {str(e)}")
            print(f"DEBUG: Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False