from django.core.management.base import BaseCommand
from authentication.models import User

class Command(BaseCommand):
    """
    Django management command to create test data for development.
    Usage: python manage.py create_test_data
    """
    
    help = 'Create test users for development and testing'

    def handle(self, *args, **options):
        """Create sample users for testing the API."""
        
        # Test user data
        test_users = [
            {
                'email': 'john.doe@example.com',
                'full_name': 'John Doe',
                'password': 'testpassword123'
            },
            {
                'email': 'jane.smith@example.com',
                'full_name': 'Jane Smith',
                'password': 'testpassword123'
            },
            {
                'email': 'mike.johnson@example.com',
                'full_name': 'Mike Johnson',
                'password': 'testpassword123'
            }
        ]
        
        created_count = 0
        
        for user_data in test_users:
            # Check if user already exists
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create_user(
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    password=user_data['password']
                )
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created test user: {user.email}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'User already exists: {user_data["email"]}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nSuccessfully created {created_count} test users!'
            )
        )
        
        if created_count > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    '\nTest user credentials:'
                    '\nEmail: john.doe@example.com'
                    '\nPassword: testpassword123'
                    '\n\nYou can use these credentials to test the API endpoints.'
                )
            )