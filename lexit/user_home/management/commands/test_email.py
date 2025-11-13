from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import ssl
import socket

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f'🔍 Testing email configuration...')
        self.stdout.write(f'📧 Sending test email to: {email}')
        self.stdout.write(f'⚙️  Email backend: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'🏠 Email host: {settings.EMAIL_HOST}')
        self.stdout.write(f'🔌 Email port: {settings.EMAIL_PORT}')
        self.stdout.write(f'🔐 Use TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'👤 Email user: {settings.EMAIL_HOST_USER}')
        
        # Test network connectivity
        try:
            self.stdout.write(f'🌐 Testing connection to {settings.EMAIL_HOST}:{settings.EMAIL_PORT}...')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            result = sock.connect_ex((settings.EMAIL_HOST, settings.EMAIL_PORT))
            sock.close()
            
            if result == 0:
                self.stdout.write('✅ Network connection successful')
            else:
                self.stdout.write(f'❌ Network connection failed: {result}')
                return
        except Exception as e:
            self.stdout.write(f'❌ Network test failed: {str(e)}')
            return
        
        try:
            send_mail(
                subject='LEXIT Email Test - Office 365 Configuration',
                message='This is a test email from your LEXIT application using Office 365 SMTP. If you received this, your email configuration is working correctly!',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ Test email sent successfully to {email}')
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Failed to send email: {str(e)}')
            )
            
            # Provide specific guidance based on error type
            error_str = str(e).lower()
            if 'certificate' in error_str or 'ssl' in error_str:
                self.stdout.write('💡 SSL Certificate issue detected. Office 365 support suggested updating CA certificates.')
            elif 'authentication' in error_str or 'login' in error_str:
                self.stdout.write('💡 Authentication issue. Check if you need an App Password for MFA-enabled accounts.')
            elif 'timeout' in error_str:
                self.stdout.write('💡 Connection timeout. Railway might be blocking SMTP ports.')
            
            self.stdout.write('Check your email configuration in settings.py and Railway environment variables')