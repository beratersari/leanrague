"""
Management command to create or reset a test admin user.
Usage: python manage.py create_test_admin

Creates a test admin user with known credentials for development/testing.
"""

from django.core.management.base import BaseCommand
from app.models.models import CustomUser, UserRole


class Command(BaseCommand):
    help = 'Create or reset a test admin user for development'

    def handle(self, *args, **options):
        email = 'admin@languagelearning.com'
        password = 'Admin123!@#'

        # Delete existing admin if exists
        CustomUser.objects.filter(email=email).delete()

        # Create new admin
        admin = CustomUser.objects.create_superuser(
            email=email,
            password=password,
            role=UserRole.ADMIN,
            first_name='Admin',
            last_name='User',
            is_verified=True,
        )

        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Test Admin Created Successfully!'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Credentials:'))
        self.stdout.write(f'  Email: {email}')
        self.stdout.write(f'  Password: {password}')
        self.stdout.write(f'  Role: Admin')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Login via: POST /api/auth/login/'))
        self.stdout.write('')
