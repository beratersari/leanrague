"""
Leaderboard service - Computes combined leaderboard scores.
N-layered architecture: Service layer.

Scoring rules:
- MCQ correct answer: POINTS_PER_MCQ_CORRECT points each
- MCQ set completion: BONUS_MCQ_SET_COMPLETE (once per completed set)
- Flashcard set completion: BONUS_FLASHCARD_SET_COMPLETE (once per completed set)
- Flashcard individual answers: NO points (learning only)

Leaderboard is computed from UserMCQProgress (times_correct) + set completion checks.
Time periods filter by last_studied_at.
"""

from typing import List, Dict, Any, Optional
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count, Q

from app.models.models import (
    CustomUser,
    UserMCQProgress,
    UserFlashcardProgress,
    MCQSet,
    FlashcardSet,
)
from app.core.logger import get_logger


# Scoring constants
POINTS_PER_MCQ_CORRECT = 10
BONUS_MCQ_SET_COMPLETE = 50
BONUS_FLASHCARD_SET_COMPLETE = 30


class LeaderboardService:
    """Service for computing and retrieving leaderboard rankings."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def _get_period_cutoff(self, period: str) -> Optional[timezone.datetime]:
        """Get the cutoff datetime for a time period."""
        now = timezone.now()
        if period == "weekly":
            return now - timedelta(days=7)
        elif period == "monthly":
            return now - timedelta(days=30)
        elif period == "yearly":
            return now - timedelta(days=365)
        else:  # all_time
            return None

    def _get_mcq_correct_points(self, period: str) -> Dict[int, int]:
        """
        Get points from MCQ correct answers per user.
        Each unique MCQ counts ONCE (if times_correct >= 1).
        Returns {user_id: points_from_correct_mcqs}
        """
        cutoff = self._get_period_cutoff(period)
        qs = UserMCQProgress.objects.all()
        if cutoff:
            qs = qs.filter(last_studied_at__gte=cutoff)

        # Count DISTINCT MCQs where user has at least 1 correct answer
        # This prevents repeated answers on the same MCQ from inflating score
        results = qs.filter(times_correct__gt=0).values('user_id').annotate(
            unique_correct=Count('mcq_id', distinct=True)
        )

        user_points = {r['user_id']: (r['unique_correct'] or 0) * POINTS_PER_MCQ_CORRECT for r in results}
        self.logger.debug(f"MCQ correct points computed for {len(user_points)} users (period={period})")
        return user_points

    def _get_completed_mcq_sets(self, period: str) -> Dict[int, int]:
        """
        Count how many MCQ sets each user has completed.
        Completion = user has times_seen > 0 for ALL MCQs in the set.
        Returns {user_id: count_of_completed_mcq_sets}
        """
        cutoff = self._get_period_cutoff(period)
        user_completed = {}

        for mcq_set in MCQSet.objects.filter(is_active=True):
            mcq_ids = list(mcq_set.mcqs.filter(is_active=True).values_list('id', flat=True))
            if not mcq_ids:
                continue

            # Users who have seen ALL MCQs in this set
            qs = UserMCQProgress.objects.filter(mcq_id__in=mcq_ids, times_seen__gt=0)
            if cutoff:
                qs = qs.filter(last_studied_at__gte=cutoff)

            # Count users who have entries for all mcqs in set
            # We need users where count of their progress = len(mcq_ids) AND all have times_seen > 0
            user_counts = qs.values('user_id').annotate(
                seen_count=Count('id')
            ).filter(seen_count=len(mcq_ids))

            for uc in user_counts:
                uid = uc['user_id']
                user_completed[uid] = user_completed.get(uid, 0) + 1

        self.logger.debug(f"MCQ set completions: {sum(user_completed.values())} total completions across users")
        return user_completed

    def _get_completed_flashcard_sets(self, period: str) -> Dict[int, int]:
        """
        Count how many flashcard sets each user has completed.
        Completion = user has times_seen > 0 for ALL flashcards in the set.
        Returns {user_id: count_of_completed_flashcard_sets}
        """
        cutoff = self._get_period_cutoff(period)
        user_completed = {}

        for fc_set in FlashcardSet.objects.filter(is_active=True):
            fc_ids = list(fc_set.flashcards.filter(is_active=True).values_list('id', flat=True))
            if not fc_ids:
                continue

            qs = UserFlashcardProgress.objects.filter(flashcard_id__in=fc_ids, times_seen__gt=0)
            if cutoff:
                qs = qs.filter(last_studied_at__gte=cutoff)

            user_counts = qs.values('user_id').annotate(
                seen_count=Count('id')
            ).filter(seen_count=len(fc_ids))

            for uc in user_counts:
                uid = uc['user_id']
                user_completed[uid] = user_completed.get(uid, 0) + 1

        self.logger.debug(f"Flashcard set completions: {sum(user_completed.values())} total completions across users")
        return user_completed

    def get_leaderboard(self, period: str = "all_time", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Compute and return the combined leaderboard.

        Args:
            period: 'weekly', 'monthly', 'yearly', or 'all_time'
            limit: Max number of users to return

        Returns:
            List of dicts: [{user_id, email, score, rank, breakdown}, ...]
        """
        self.logger.info(f"get_leaderboard called: period={period}, limit={limit}")

        # 1. MCQ correct answer points
        mcq_points = self._get_mcq_correct_points(period)

        # 2. MCQ set completion bonus
        mcq_set_completions = self._get_completed_mcq_sets(period)
        mcq_set_bonus = {uid: cnt * BONUS_MCQ_SET_COMPLETE for uid, cnt in mcq_set_completions.items()}

        # 3. Flashcard set completion bonus
        fc_set_completions = self._get_completed_flashcard_sets(period)
        fc_set_bonus = {uid: cnt * BONUS_FLASHCARD_SET_COMPLETE for uid, cnt in fc_set_completions.items()}

        # 4. Combine all scores per user
        all_user_ids = set(mcq_points.keys()) | set(mcq_set_bonus.keys()) | set(fc_set_bonus.keys())
        scores = {}

        for uid in all_user_ids:
            score = (
                mcq_points.get(uid, 0)
                + mcq_set_bonus.get(uid, 0)
                + fc_set_bonus.get(uid, 0)
            )
            scores[uid] = {
                'score': score,
                'mcq_correct_points': mcq_points.get(uid, 0),
                'mcq_set_bonus': mcq_set_bonus.get(uid, 0),
                'flashcard_set_bonus': fc_set_bonus.get(uid, 0),
            }

        # 5. Sort by score descending
        sorted_users = sorted(scores.items(), key=lambda x: x[1]['score'], reverse=True)

        # 6. Build result with user info and rank
        result = []
        rank = 1
        prev_score = None
        actual_rank = 1

        for idx, (uid, data) in enumerate(sorted_users[:limit]):
            try:
                user = CustomUser.objects.get(id=uid, is_active=True)
            except CustomUser.DoesNotExist:
                continue

            # Handle ties (same score = same rank)
            if prev_score is not None and data['score'] < prev_score:
                actual_rank = rank
            prev_score = data['score']
            rank = idx + 1  # position in list

            result.append({
                'user_id': uid,
                'email': user.email,
                'full_name': user.full_name,
                'score': data['score'],
                'rank': actual_rank,
                'breakdown': {
                    'mcq_correct_points': data['mcq_correct_points'],
                    'mcq_set_bonus': data['mcq_set_bonus'],
                    'flashcard_set_bonus': data['flashcard_set_bonus'],
                }
            })

        self.logger.info(f"Leaderboard computed: {len(result)} users (period={period})")
        return result

    def get_user_rank(self, user_id: int, period: str = "all_time") -> Optional[Dict[str, Any]]:
        """
        Get a specific user's rank and score.
        Returns None if user has no score.
        """
        self.logger.debug(f"get_user_rank called: user_id={user_id}, period={period}")
        leaderboard = self.get_leaderboard(period=period, limit=10000)

        for entry in leaderboard:
            if entry['user_id'] == user_id:
                return entry

        return None
