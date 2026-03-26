"""
Management command to create mock user follows for testing.
Usage: python manage.py create_mock_follows

Creates follow relationships between users.
"""

from django.core.management.base import BaseCommand
import random

from app.models.models import CustomUser, UserFollow


class Command(BaseCommand):
    help = 'Create mock user follows for testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Creating mock follows...'))

        users = list(CustomUser.objects.filter(is_active=True))
        if len(users) < 2:
            self.stdout.write(self.style.ERROR('Need at least 2 users. Run load_mock_data first.'))
            return

        total_follows = 0

        # Each user follows 1-3 other users randomly
        for user in users:
            # Pick random users to follow (not self)
            candidates = [u for u in users if u.id != user.id]
            num_follows = min(random.randint(1, 3), len(candidates))
            to_follow = random.sample(candidates, num_follows)

            for target in to_follow:
                follow, created = UserFollow.objects.get_or_create(
                    follower=user,
                    following=target,
                )
                if created:
                    total_follows += 1
                    self.stdout.write(f'  ✓ {user.email} follows {target.email}')

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total follows created: {total_follows}'))

        # Show stats
        self.stdout.write('')
        self.stdout.write('Follow stats per user:')
        for user in users[:5]:
            followers = UserFollow.objects.filter(following=user).count()
            following = UserFollow.objects.filter(follower=user).count()
            self.stdout.write(f'  {user.email}: {followers} followers, {following} following')

        self.stdout.write(self.style.SUCCESS('Done!'))
