from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'List all superuser accounts'

    def handle(self, *args, **options):
        superusers = User.objects.filter(is_superuser=True)
        
        if superusers:
            self.stdout.write(self.style.SUCCESS('Superusers found:'))
            for user in superusers:
                self.stdout.write(f'Username: {user.username}')
                self.stdout.write(f'Email: {user.email}')
                self.stdout.write(f'Active: {user.is_active}')
                self.stdout.write(f'Last login: {user.last_login}')
                self.stdout.write('-' * 30)
        else:
            self.stdout.write(self.style.WARNING('No superusers found'))