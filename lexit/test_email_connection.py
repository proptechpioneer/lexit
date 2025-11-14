#!/usr/bin/env python
"""
Alternative email test using Django's get_connection
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

from django.core.mail import send_mail, EmailMessage, get_connection
from django.conf import settings

def test_email_with_connection():
    """Test email functionality with explicit connection"""
    print("🔧 Testing Email Configuration with Django Connection...")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()
    
    # Get a connection using Django's settings
    try:
        print("🔗 Creating Django email connection...")
        connection = get_connection()
        print("✅ Connection created successfully!")
        
        # Test connection
        print("🔌 Testing connection...")
        connection.open()
        print("✅ Connection opened successfully!")
        connection.close()
        print("✅ Connection closed successfully!")
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("ℹ️  This indicates an issue with the email server configuration.")
        return
    
    # Test 1: Simple send_mail with connection
    try:
        print("📧 Test 1: Sending simple test email with connection...")
        result = send_mail(
            subject='LEXIT Email Test - Simple (Connection)',
            message='This is a test email from your LEXIT application using Django connection handling.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['ashley.osborne@prs-im.co.uk'],
            fail_silently=False,
            connection=connection,
        )
        print(f"✅ Simple email sent successfully! Result: {result}")
    except Exception as e:
        print(f"❌ Simple email failed: {e}")
    
    print()
    
    # Test 2: HTML EmailMessage with connection
    try:
        print("📧 Test 2: Sending HTML test email with connection...")
        msg = EmailMessage(
            subject='LEXIT Email Test - HTML (Connection)',
            body="""
            <html>
            <body>
                <h2>🎉 LEXIT Email Test</h2>
                <p>This is an <strong>HTML test email</strong> from your LEXIT application.</p>
                <p>Using Django connection handling for better compatibility!</p>
                <hr>
                <small>Sent from LEXIT Django Application</small>
            </body>
            </html>
            """,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['ashley.osborne@prs-im.co.uk'],
            connection=connection,
        )
        msg.content_subtype = "html"
        result = msg.send()
        print(f"✅ HTML email sent successfully! Result: {result}")
    except Exception as e:
        print(f"❌ HTML email failed: {e}")

if __name__ == '__main__':
    test_email_with_connection()