"""
Practice service - Spaced repetition practice logic.
N-layered architecture: Service layer.
"""

from typing import List, Dict, Any
from django.utils import timezone
from django.db.models import Q

from app.models.models import (
    Flashcard,
    MCQ,
    UserFlashcardProgress,
    UserMCQProgress,
)
from app.core.logger import get_logger
from app.services.leaderboard_service import POINTS_PER_MCQ_CORRECT


class PracticeService:
    """Service for spaced repetition practice sessions."""

    def __init__(self, user):
        self.user = user
        self.logger = get_logger(__name__)

    def get_practice_flashcards(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get flashcards for practice sorted by ease factor and due date.
        Returns cards that are due or have no progress record.
        """
        self.logger.debug(f"get_practice_flashcards called for user_id={self.user.id}, email={self.user.email}, count={count}")
        today = timezone.now().date()

        # Get IDs of cards user has progress for
        progress_ids = set(
            UserFlashcardProgress.objects.filter(user=self.user)
            .values_list('flashcard_id', flat=True)
        )

        # Due cards: have progress and next_review_date <= today
        due_progress = UserFlashcardProgress.objects.filter(
            user=self.user,
            next_review_date__lte=today
        ).select_related('flashcard').order_by('ease_factor', 'next_review_date')[:count]

        # New cards: no progress record (not studied yet)
        new_cards = Flashcard.objects.filter(
            is_active=True
        ).exclude(
            id__in=progress_ids
        ).order_by('?')[:max(0, count - due_progress.count())]

        results = []

        # Add due cards first
        for prog in due_progress:
            card = prog.flashcard
            results.append({
                'type': 'flashcard',
                'id': card.id,
                'front': card.front,
                'back': card.back,
                'hint': card.hint,
                'flashcard_set_id': card.flashcard_set_id,
                'is_premium': card.is_premium,
                'ease_factor': prog.ease_factor,
                'interval_days': prog.interval_days,
                'times_seen': prog.times_seen,
                'times_correct': prog.times_correct,
                'last_rating': prog.last_rating,
                'next_review_date': prog.next_review_date,
                'progress_id': prog.id,
            })

        # Add new cards
        for card in new_cards:
            results.append({
                'type': 'flashcard',
                'id': card.id,
                'front': card.front,
                'back': card.back,
                'hint': card.hint,
                'flashcard_set_id': card.flashcard_set_id,
                'is_premium': card.is_premium,
                'ease_factor': 2.5,  # Default for new cards
                'interval_days': 1,
                'times_seen': 0,
                'times_correct': 0,
                'last_rating': None,
                'next_review_date': None,
                'progress_id': None,
            })

        self.logger.info(f"Retrieved {len(results[:count])} practice flashcards for user_id={self.user.id}, email={self.user.email}")
        return results[:count]

    def get_practice_mcqs(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get MCQs for practice sorted by ease factor and due date.
        Returns questions that are due or have no progress record.
        """
        self.logger.debug(f"get_practice_mcqs called for user {self.user.id}, count={count}")
        today = timezone.now().date()

        # Get IDs of MCQs user has progress for
        progress_ids = set(
            UserMCQProgress.objects.filter(user=self.user)
            .values_list('mcq_id', flat=True)
        )

        # Due MCQs
        due_progress = UserMCQProgress.objects.filter(
            user=self.user,
            next_review_date__lte=today
        ).select_related('mcq').order_by('ease_factor', 'next_review_date')[:count]

        # New MCQs
        new_mcqs = MCQ.objects.filter(
            is_active=True
        ).exclude(
            id__in=progress_ids
        ).order_by('?')[:max(0, count - due_progress.count())]

        results = []

        for prog in due_progress:
            mcq = prog.mcq
            results.append({
                'type': 'mcq',
                'id': mcq.id,
                'question': mcq.question,
                'option_a': mcq.option_a,
                'option_b': mcq.option_b,
                'option_c': mcq.option_c,
                'option_d': mcq.option_d,
                'correct_option': mcq.correct_option,
                'explanation': mcq.explanation,
                'hint': mcq.hint,
                'mcq_set_id': mcq.mcq_set_id,
                'is_premium': mcq.is_premium,
                'ease_factor': prog.ease_factor,
                'interval_days': prog.interval_days,
                'times_seen': prog.times_seen,
                'times_correct': prog.times_correct,
                'last_rating': prog.last_rating,
                'next_review_date': prog.next_review_date,
                'progress_id': prog.id,
            })

        for mcq in new_mcqs:
            results.append({
                'type': 'mcq',
                'id': mcq.id,
                'question': mcq.question,
                'option_a': mcq.option_a,
                'option_b': mcq.option_b,
                'option_c': mcq.option_c,
                'option_d': mcq.option_d,
                'correct_option': mcq.correct_option,
                'explanation': mcq.explanation,
                'hint': mcq.hint,
                'mcq_set_id': mcq.mcq_set_id,
                'is_premium': mcq.is_premium,
                'ease_factor': 2.5,
                'interval_days': 1,
                'times_seen': 0,
                'times_correct': 0,
                'last_rating': None,
                'next_review_date': None,
                'progress_id': None,
            })

        self.logger.info(f"Retrieved {len(results[:count])} practice MCQs for user {self.user.id}")
        return results[:count]

    def get_practice_mixed(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get a mix of flashcards and MCQs for practice.
        Returns questions sorted by ease factor (lower = harder first).
        """
        self.logger.debug(f"get_practice_mixed called for user {self.user.id}, count={count}")
        flashcards = self.get_practice_flashcards(count)
        mcqs = self.get_practice_mcqs(count)

        # Combine and sort by ease factor (lower first = harder)
        all_items = flashcards + mcqs
        all_items.sort(key=lambda x: (x.get('ease_factor', 2.5), x.get('next_review_date') or timezone.now().date()))

        self.logger.info(f"Retrieved {len(all_items[:count])} mixed practice items for user {self.user.id}")
        return all_items[:count]

    def submit_flashcard_rating(self, flashcard_id: int, rating: str) -> Dict[str, Any]:
        """Submit a rating for a flashcard and update SRS."""
        self.logger.info(f"submit_flashcard_rating: user_id={self.user.id}, email={self.user.email}, flashcard={flashcard_id}, rating={rating}")
        from app.models.models import Flashcard

        flashcard = Flashcard.objects.filter(id=flashcard_id, is_active=True).first()
        if not flashcard:
            self.logger.warning(f"Flashcard {flashcard_id} not found for rating")
            return {'error': 'Flashcard not found'}

        progress, created = UserFlashcardProgress.objects.get_or_create(
            user=self.user,
            flashcard=flashcard,
            defaults={
                'ease_factor': 2.5,
                'interval_days': 1,
            }
        )

        valid_ratings = ['again', 'hard', 'good', 'easy']
        if rating not in valid_ratings:
            self.logger.warning(f"Invalid rating '{rating}' submitted for flashcard {flashcard_id}")
            return {'error': f'Invalid rating. Use one of: {valid_ratings}'}

        progress.update_srs(rating)

        self.logger.debug(f"Flashcard {flashcard_id} SRS updated: ease_factor={progress.ease_factor}, interval={progress.interval_days}")
        return {
            'success': True,
            'flashcard_id': flashcard_id,
            'rating': rating,
            'ease_factor': progress.ease_factor,
            'interval_days': progress.interval_days,
            'next_review_date': progress.next_review_date,
            'times_seen': progress.times_seen,
        }

    def submit_mcq_answer(self, mcq_id: int, user_answer: str) -> Dict[str, Any]:
        """
        Submit MCQ answer. System automatically:
        - Checks correctness
        - Updates times_seen / times_correct
        - Adjusts ease factor (wrong=lower, correct=normal)
        No separate rating needed.
        """
        self.logger.info(f"submit_mcq_answer: user_id={self.user.id}, email={self.user.email}, mcq={mcq_id}, answer={user_answer}")
        from app.models.models import MCQ

        mcq = MCQ.objects.filter(id=mcq_id, is_active=True).first()
        if not mcq:
            self.logger.warning(f"MCQ {mcq_id} not found for answer submission")
            return {'error': 'MCQ not found'}

        progress, created = UserMCQProgress.objects.get_or_create(
            user=self.user,
            mcq=mcq,
            defaults={
                'ease_factor': 2.5,
                'interval_days': 1,
            }
        )

        # Check correctness
        is_correct = mcq.check_answer(user_answer)

        # Update tracking counters
        progress.times_seen += 1
        if is_correct:
            progress.times_correct += 1

        # Apply SRS based on correctness (no user rating needed)
        if is_correct:
            # Correct → apply "good" SRS (normal progression)
            progress.update_srs('good')
        else:
            # Wrong → apply "again" SRS (reset, show more often)
            progress.update_srs('again')

        progress.last_studied_at = __import__('django.utils.timezone', fromlist=['now']).now()
        progress.save()

        self.logger.debug(f"MCQ {mcq_id} answer processed: correct={is_correct}, accuracy={round(progress.times_correct / progress.times_seen * 100, 1) if progress.times_seen else 0}%")

        # Points earned for correct answer
        points_earned = POINTS_PER_MCQ_CORRECT if is_correct else 0

        return {
            'success': True,
            'mcq_id': mcq_id,
            'user_answer': user_answer.upper(),
            'is_correct': is_correct,
            'correct_option': mcq.correct_option,
            'correct_answer': mcq.correct_answer,
            'ease_factor': progress.ease_factor,
            'interval_days': progress.interval_days,
            'next_review_date': progress.next_review_date,
            'times_seen': progress.times_seen,
            'times_correct': progress.times_correct,
            'accuracy': round(progress.times_correct / progress.times_seen * 100, 1) if progress.times_seen else 0,
            'points_earned': points_earned,
        }
