#!/usr/bin/env python
"""
Test script to verify email configuration
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lexit.settings')
django.setup()

from django.core.mail import send_mail, EmailMessage
from django.conf import settings
import ssl
import certifi

def test_email():
    """Test email functionality"""
    print("🔧 Testing Email Configuration...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Test 1: Simple send_mail
    try:
        print("📧 Test 1: Sending simple test email...")
        result = send_mail(
            subject='LEXIT Email Test - Simple',
            message='This is a test email from your LEXIT application to verify email configuration is working correctly.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['ashley.osborne@prs-im.co.uk'],
            fail_silently=False,
        )
        print(f"✅ Simple email sent successfully! Result: {result}")
    except Exception as e:
        print(f"❌ Simple email failed: {e}")
        print("ℹ️  This might be due to SSL certificate issues or authentication problems.")
    
    print()
    
    # Test 2: HTML EmailMessage
    try:
        print("📧 Test 2: Sending HTML test email...")
        msg = EmailMessage(
            subject='LEXIT Email Test - HTML',
            body="""
            <html>
            <body>
                <h2>🎉 LEXIT Email Test</h2>
                <p>This is an <strong>HTML test email</strong> from your LEXIT application.</p>
                <p>If you're seeing this, your email configuration is working correctly!</p>
                <hr>
                <small>Sent from LEXIT Django Application</small>
            </body>
            </html>
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['ashley.osborne@prs-im.co.uk'],
        )
        msg.content_subtype = "html"
        result = msg.send()
        print(f"✅ HTML email sent successfully! Result: {result}")
    except Exception as e:
        print(f"❌ HTML email failed: {e}")
        print("ℹ️  This might be due to SSL certificate issues or authentication problems.")

if __name__ == '__main__':
    test_email()