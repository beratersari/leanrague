"""
Management command to generate mock SRS submissions for all users.
Usage: python manage.py generate_mock_submissions

Creates at least 200 submission records per user (flashcard + MCQ progress).
Distributes last_studied_at across time periods for leaderboard testing.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random

from app.models.models import (
    CustomUser,
    Flashcard,
    MCQ,
    FlashcardSet,
    MCQSet,
    UserFlashcardProgress,
    UserMCQProgress,
    Rating,
)


class Command(BaseCommand):
    help = 'Generate mock SRS submissions (at least 200 per user)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--leaderboard',
            action='store_true',
            help='Generate leaderboard-friendly data with varied time periods and set completions',
        )

    def _random_date_in_period(self, period: str) -> timezone.datetime:
        """Return a random date within the given period."""
        now = timezone.now()
        if period == 'weekly':
            days = random.randint(0, 7)
        elif period == 'monthly':
            days = random.randint(8, 30)
        elif period == 'yearly':
            days = random.randint(31, 365)
        else:  # all_time (older than 1 year)
            days = random.randint(366, 500)
        return now - timedelta(days=days)

    def handle(self, *args, **options):
        leaderboard_mode = options.get('leaderboard', False)
        self.stdout.write(self.style.WARNING('Generating mock SRS submissions...'))
        if leaderboard_mode:
            self.stdout.write(self.style.WARNING('  (Leaderboard mode: varied time periods + set completions)'))

        users = CustomUser.objects.filter(role='user')
        all_flashcards = list(Flashcard.objects.filter(is_active=True))
        all_mcqs = list(MCQ.objects.filter(is_active=True))
        all_flashcard_sets = list(FlashcardSet.objects.filter(is_active=True))
        all_mcq_sets = list(MCQSet.objects.filter(is_active=True))

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

            # Determine which time periods this user gets (for leaderboard variety)
            # Spread users across periods
            user_periods = ['weekly', 'monthly', 'yearly', 'all_time']
            # Each user gets a mix, weighted toward recent
            period_weights = [0.4, 0.3, 0.2, 0.1]  # 40% weekly, 30% monthly, etc.

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
                        'times_seen': random.randint(1, 15),
                        'times_correct': random.randint(0, 12),
                    }
                )
                
                if created:
                    # In leaderboard mode, spread dates across all periods
                    if leaderboard_mode:
                        period = random.choices(user_periods, weights=period_weights)[0]
                        progress.last_studied_at = self._random_date_in_period(period)
                    else:
                        days_ago = random.randint(0, 30)
                        progress.last_studied_at = timezone.now() - timedelta(days=days_ago)
                    
                    progress.next_review_date = timezone.now().date() + timedelta(
                        days=random.randint(-5, 15)
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
                        'times_seen': random.randint(1, 15),
                        'times_correct': random.randint(0, 12),
                    }
                )
                
                if created:
                    if leaderboard_mode:
                        period = random.choices(user_periods, weights=period_weights)[0]
                        progress.last_studied_at = self._random_date_in_period(period)
                    else:
                        days_ago = random.randint(0, 30)
                        progress.last_studied_at = timezone.now() - timedelta(days=days_ago)
                    
                    progress.next_review_date = timezone.now().date() + timedelta(
                        days=random.randint(-5, 15)
                    )
                    progress.last_rating = random.choice([r[0] for r in Rating.choices])
                    progress.save()
                    user_submissions += 1

            # In leaderboard mode: ensure some users complete at least one full set
            if leaderboard_mode and random.random() < 0.6:  # 60% chance to complete a set
                # Complete one MCQ set
                if all_mcq_sets:
                    mcq_set = random.choice(all_mcq_sets)
                    mcqs_in_set = list(mcq_set.mcqs.filter(is_active=True))
                    for mcq in mcqs_in_set:
                        progress, _ = UserMCQProgress.objects.get_or_create(
                            user=user,
                            mcq=mcq,
                            defaults={
                                'ease_factor': 2.0,
                                'interval_days': 5,
                                'times_seen': random.randint(1, 5),
                                'times_correct': random.randint(1, 4),
                            }
                        )
                        # Ensure recent enough to count in monthly/yearly
                        progress.last_studied_at = timezone.now() - timedelta(days=random.randint(1, 180))
                        progress.save()
                        if progress.pk:  # new record
                            user_submissions += 1

                # Complete one flashcard set
                if all_flashcard_sets:
                    fc_set = random.choice(all_flashcard_sets)
                    fcs_in_set = list(fc_set.flashcards.filter(is_active=True))
                    for fc in fcs_in_set:
                        progress, _ = UserFlashcardProgress.objects.get_or_create(
                            user=user,
                            flashcard=fc,
                            defaults={
                                'ease_factor': 2.0,
                                'interval_days': 5,
                                'times_seen': random.randint(1, 5),
                                'times_correct': random.randint(1, 4),
                            }
                        )
                        progress.last_studied_at = timezone.now() - timedelta(days=random.randint(1, 180))
                        progress.save()
                        if progress.pk:
                            user_submissions += 1

            self.stdout.write(
                self.style.SUCCESS(f'    ✓ {user_submissions} submissions created for {user.email}')
            )
            total_submissions += user_submissions

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Total submissions created: {total_submissions}'))
        if leaderboard_mode:
            self.stdout.write(self.style.SUCCESS('Leaderboard mode enabled: varied periods + set completions!'))
        self.stdout.write(self.style.SUCCESS('Done!'))
