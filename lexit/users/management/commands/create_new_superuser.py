from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

class Command(BaseCommand):
    help = 'Create a new superuser account'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')

    def handle(self, *args, **options):
        username = options.get('username') or 'ashley'
        email = options.get('email') or 'ashley.osborne@prs-im.co.uk'
        password = options.get('password') or 'LexitAdmin2024!'
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists. Use --username to specify a different one.')
            )
            return
            
        if User.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.WARNING(f'User with email "{email}" already exists.')
            )
            
        try:
            # Validate password
            validate_password(password)
            
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Superuser created successfully!')
            )
            self.stdout.write(f'Username: {username}')
            self.stdout.write(f'Email: {email}')
            self.stdout.write(f'Password: {password}')
            self.stdout.write(f'Login URL: https://lexit.tech/admin/')
            
        except ValidationError as e:
            self.stdout.write(
                self.style.ERROR(f'Password validation failed: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {e}')
            )