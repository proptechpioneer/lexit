from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings

class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email address to send test email to')

    def handle(self, *args, **options):
        email = options['email']
        
        self.stdout.write(f'Sending test email to: {email}')
        self.stdout.write(f'Email backend: {settings.EMAIL_BACKEND}')
        
        try:
            send_mail(
                subject='LEXIT Email Test',
                message='This is a test email from your LEXIT application. If you received this, your email configuration is working correctly!',
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
            self.stdout.write('Check your email configuration in settings.py and .env file')