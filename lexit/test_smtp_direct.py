#!/usr/bin/env python
"""
Email test with SSL bypass for local testing
"""
import os
import sys
import django
from pathlib import Path
import ssl
import smtplib

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexit.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings

def test_direct_smtp():
    """Test direct SMTP connection bypassing SSL verification"""
    print("🔧 Testing Direct SMTP Connection...")
    
    try:
        print("📧 Testing direct SMTP connection to Office 365...")
        
        # Create SMTP connection with relaxed SSL
        server = smtplib.SMTP('smtp.office365.com', 587)
        server.starttls()  # Enable TLS
        
        # Login with App Password
        print("🔑 Logging in with App Password...")
        server.login('info@lexit.tech', 'stnvshcdjcsdydvv')
        print("✅ Login successful!")
        
        # Send test email
        from_email = 'info@lexit.tech'
        to_email = 'ashley.osborne@prs-im.co.uk'
        
        message = """Subject: LEXIT Email Test - Direct SMTP
From: info@lexit.tech
To: ashley.osborne@prs-im.co.uk

This is a direct SMTP test from your LEXIT application.

If you receive this email, your Office 365 App Password is working correctly!

Sent from LEXIT Django Application
"""
        
        print("📤 Sending test email...")
        server.sendmail(from_email, [to_email], message)
        print("✅ Email sent successfully!")
        
        server.quit()
        print("✅ SMTP connection closed.")
        
    except Exception as e:
        print(f"❌ Direct SMTP test failed: {e}")

def test_django_email():
    """Test Django email with modified settings"""
    print("\n🔧 Testing Django Email (bypassing SSL verification)...")
    
    # Temporarily modify Django's SMTP backend to bypass SSL issues
    import django.core.mail.backends.smtp
    original_get_connection = django.core.mail.backends.smtp.EmailBackend._get_connection
    
    def patched_get_connection(self):
        """Patched connection with relaxed SSL"""
        connection = original_get_connection(self)
        # Don't verify SSL certificates for testing
        if hasattr(connection, '_context'):
            connection._context = ssl.create_default_context()
            connection._context.check_hostname = False
            connection._context.verify_mode = ssl.CERT_NONE
        return connection
    
    # Apply patch
    django.core.mail.backends.smtp.EmailBackend._get_connection = patched_get_connection
    
    try:
        print("📧 Sending Django email with SSL bypass...")
        result = send_mail(
            subject='LEXIT Email Test - Django (SSL Bypass)',
            message='This is a Django email test with SSL bypass.\n\nIf you receive this, Django email is working!',
            from_email='info@lexit.tech',
            recipient_list=['ashley.osborne@prs-im.co.uk'],
            fail_silently=False,
        )
        print(f"✅ Django email sent successfully! Result: {result}")
        
    except Exception as e:
        print(f"❌ Django email failed: {e}")
    
    finally:
        # Restore original method
        django.core.mail.backends.smtp.EmailBackend._get_connection = original_get_connection

if __name__ == '__main__':
    test_direct_smtp()
    test_django_email()