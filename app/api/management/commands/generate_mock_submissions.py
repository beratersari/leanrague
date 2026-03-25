"""
Management command to generate mock SRS submissions for all users.
Usage: python manage.py generate_mock_submissions

Creates at least 200 submission records per user (flashcard + MCQ progress).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from app.models.models import (
    CustomUser,
    Flashcard,
    MCQ,
    UserFlashcardProgress,
    UserMCQProgress,
    Rating,
)


class Command(BaseCommand):
    help = 'Generate mock SRS submissions (at least 200 per user)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Generating mock SRS submissions...'))

        users = CustomUser.objects.filter(role='user')
        all_flashcards = list(Flashcard.objects.filter(is_active=True))
        all_mcqs = list(MCQ.objects.filter(is_active=True))

        if not all_flashcards:
            self.stdout.write(self.style.ERROR('No flashcards found. Run load_mock_data first.'))
            return

        if not all_mcqs:
            self.stdout.write(self.style.ERROR('No MCQs found. Run load_mock_data first.'))
            return

        total_submissions = 0

        for user in users:
            user_submissions = 0
            self.stdout.write(f'  Processing user: {user.email}')

            # Generate flashcard progress (at least 100 per user)
            num_flashcards = min(150, len(all_flashcards))
            selected_flashcards = random.sample(all_flashcards, num_flashcards)
            
            for flashcard in selected_flashcards:
                # Create or update progress
                progress, created = UserFlashcardProgress.objects.get_or_create(
                    user=user,
                    flashcard=flashcard,
                    defaults={
                        'ease_factor': round(random.uniform(1.3, 2.5), 2),
                        'interval_days': random.choice([1, 1, 1, 6, 6, 10, 15]),
                        'times_seen': random.randint(1, 10),
                        'times_correct': random.randint(0, 8),
                    }
                )
                
                if created:
                    # Randomize review dates (some due, some not)
                    days_ago = random.randint(0, 30)
                    progress.last_studied_at = timezone.now() - timedelta(days=days_ago)
                    progress.next_review_date = timezone.now().date() + timedelta(
                        days=random.randint(-5, 15)  # Some due, some future
                    )
                    progress.last_rating = random.choice([r[0] for r in Rating.choices])
                    progress.save()
                    user_submissions += 1

            # Generate MCQ progress (at least 100 per user)
            num_mcqs = min(150, len(all_mcqs))
            selected_mcqs = random.sample(all_mcqs, num_mcqs)
            
            for mcq in selected_mcqs:
                progress, created = UserMCQProgress.objects.get_or_create(
                    user=user,
                    mcq=mcq,
                    defaults={
                        'ease_factor': round(random.uniform(1.3, 2.5), 2),
                        'interval_days': random.choice([1, 1, 1, 6, 6, 10, 15]),
                        'times_seen': random.randint(1, 10),
                        'times_correct': random.randint(0, 8),
                    }
                )
                
                if created:
                    days_ago = random.randint(0, 30)
                    progress.last_studied_at = timezone.now() - timedelta(days=days_ago)
                    progress.next_review_date = timezone.now().date() + timedelta(
                        days=random.randint(-5, 15)
                    )
                    progress.last_rating = random.choice([r[0] for r in Rating.choices])
                    progress.save()
                    user_submissions += 1

            self.stdout.write(
                self.style.SUCCESS(f'    ✓ {user_submissions} submissions created for {user.email}')
            )
            total_submissions += user_submissions

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total submissions created: {total_submissions}'))
        self.stdout.write(self.style.SUCCESS('Done!'))
