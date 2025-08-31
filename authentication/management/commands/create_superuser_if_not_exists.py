from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser if one does not exist'

    def handle(self, *args, **options):
        email = os.environ.get('SUPERUSER_EMAIL')
        password = os.environ.get('SUPERUSER_PASSWORD')
        full_name = os.environ.get('SUPERUSER_NAME')
        
        if not all([email, password, full_name]):
            self.stdout.write(
                self.style.WARNING('Superuser creation skipped: SUPERUSER_EMAIL, SUPERUSER_PASSWORD, or SUPERUSER_NAME not set')
            )
            return
        
        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(
                email=email,
                full_name=full_name,
                password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f'Superuser created: {email}')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'Superuser already exists: {email}')
            )