"""
Gamification service - XP, Level, and Badge system (computed/derived).
N-layered architecture: Service layer.

Recommendation 1: Computed/Derived (no new models, no migrations)
- XP computed on-the-fly from UserMCQProgress, UserFlashcardProgress
- Level computed from XP via formula
- Badges evaluated on-demand against current progress

This keeps everything stateless and always in sync with progress data.
"""

from typing import Dict, Any, List, Optional
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from app.models.models import (
    CustomUser,
    UserMCQProgress,
    UserFlashcardProgress,
    MCQSet,
    FlashcardSet,
)
from app.core.logger import get_logger


# XP Constants
XP_PER_UNIQUE_MCQ_CORRECT = 10
XP_PER_MCQ_SET_COMPLETE = 25
XP_PER_FLASHCARD_SET_COMPLETE = 15

# Level formula: level = floor(sqrt(xp / 100)) + 1 (level 1 starts at 0 XP)
# Or simpler: level = 1 + xp // 100 (100 XP per level)
XP_PER_LEVEL = 100


# Badge definitions (static, no DB)
# Each badge has: id, name, description, icon, condition, progress_key, progress_target
BADGE_DEFINITIONS = [
    {
        'id': 'first_mcq',
        'name': 'First Steps',
        'description': 'Answer your first MCQ correctly',
        'icon': '🎯',
        'condition': lambda stats: stats['unique_mcqs_correct'] >= 1,
        'progress_key': 'unique_mcqs_correct',
        'progress_target': 1,
    },
    {
        'id': 'mcq_10',
        'name': 'Quick Learner',
        'description': 'Answer 10 unique MCQs correctly',
        'icon': '📚',
        'condition': lambda stats: stats['unique_mcqs_correct'] >= 10,
        'progress_key': 'unique_mcqs_correct',
        'progress_target': 10,
    },
    {
        'id': 'mcq_50',
        'name': 'Quiz Master',
        'description': 'Answer 50 unique MCQs correctly',
        'icon': '🏆',
        'condition': lambda stats: stats['unique_mcqs_correct'] >= 50,
        'progress_key': 'unique_mcqs_correct',
        'progress_target': 50,
    },
    {
        'id': 'mcq_100',
        'name': 'Centurion',
        'description': 'Answer 100 unique MCQs correctly',
        'icon': '💯',
        'condition': lambda stats: stats['unique_mcqs_correct'] >= 100,
        'progress_key': 'unique_mcqs_correct',
        'progress_target': 100,
    },
    {
        'id': 'mcq_set_1',
        'name': 'Set Starter',
        'description': 'Complete your first MCQ set',
        'icon': '📋',
        'condition': lambda stats: stats['mcq_sets_completed'] >= 1,
        'progress_key': 'mcq_sets_completed',
        'progress_target': 1,
    },
    {
        'id': 'mcq_set_5',
        'name': 'Set Master',
        'description': 'Complete 5 MCQ sets',
        'icon': '📖',
        'condition': lambda stats: stats['mcq_sets_completed'] >= 5,
        'progress_key': 'mcq_sets_completed',
        'progress_target': 5,
    },
    {
        'id': 'fc_set_1',
        'name': 'Flashcard Beginner',
        'description': 'Complete your first flashcard set',
        'icon': '🗂️',
        'condition': lambda stats: stats['flashcard_sets_completed'] >= 1,
        'progress_key': 'flashcard_sets_completed',
        'progress_target': 1,
    },
    {
        'id': 'fc_set_5',
        'name': 'Flashcard Pro',
        'description': 'Complete 5 flashcard sets',
        'icon': '🗃️',
        'condition': lambda stats: stats['flashcard_sets_completed'] >= 5,
        'progress_key': 'flashcard_sets_completed',
        'progress_target': 5,
    },
]


class GamificationService:
    """Service for computing XP, Level, and Badges (all derived from progress)."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def _get_user_stats(self, user_id: int) -> Dict[str, int]:
        """
        Compute stats for a user from their progress records.
        Returns dict with counts used for XP, levels, and badges.
        """
        # Unique MCQs answered correctly (times_correct > 0)
        unique_mcqs_correct = UserMCQProgress.objects.filter(
            user_id=user_id,
            times_correct__gt=0
        ).values('mcq_id').distinct().count()

        # MCQ set completions: count sets where user has seen ALL MCQs
        mcq_sets_completed = 0
        for mcq_set in MCQSet.objects.filter(is_active=True):
            mcq_ids = list(mcq_set.mcqs.filter(is_active=True).values_list('id', flat=True))
            if not mcq_ids:
                continue
            seen_count = UserMCQProgress.objects.filter(
                user_id=user_id,
                mcq_id__in=mcq_ids,
                times_seen__gt=0
            ).count()
            if seen_count == len(mcq_ids):
                mcq_sets_completed += 1

        # Flashcard set completions
        flashcard_sets_completed = 0
        for fc_set in FlashcardSet.objects.filter(is_active=True):
            fc_ids = list(fc_set.flashcards.filter(is_active=True).values_list('id', flat=True))
            if not fc_ids:
                continue
            seen_count = UserFlashcardProgress.objects.filter(
                user_id=user_id,
                flashcard_id__in=fc_ids,
                times_seen__gt=0
            ).count()
            if seen_count == len(fc_ids):
                flashcard_sets_completed += 1

        return {
            'unique_mcqs_correct': unique_mcqs_correct,
            'mcq_sets_completed': mcq_sets_completed,
            'flashcard_sets_completed': flashcard_sets_completed,
        }

    def get_xp(self, user_id: int) -> int:
        """
        Compute total XP for a user.
        XP = (unique MCQs correct * 10) + (MCQ sets * 25) + (Flashcard sets * 15)
        """
        stats = self._get_user_stats(user_id)
        xp = (
            stats['unique_mcqs_correct'] * XP_PER_UNIQUE_MCQ_CORRECT
            + stats['mcq_sets_completed'] * XP_PER_MCQ_SET_COMPLETE
            + stats['flashcard_sets_completed'] * XP_PER_FLASHCARD_SET_COMPLETE
        )
        self.logger.debug(f"User {user_id} XP: {xp} (stats={stats})")
        return xp

    def get_level(self, user_id: int) -> int:
        """
        Compute level from XP.
        Formula: level = 1 + xp // 100 (100 XP per level)
        """
        xp = self.get_xp(user_id)
        level = 1 + xp // XP_PER_LEVEL
        return level

    def get_xp_to_next_level(self, user_id: int) -> int:
        """
        XP needed to reach the next level.
        """
        xp = self.get_xp(user_id)
        current_level = 1 + xp // XP_PER_LEVEL
        xp_for_next = current_level * XP_PER_LEVEL
        return max(0, xp_for_next - xp)

    def get_level_progress(self, user_id: int) -> Dict[str, Any]:
        """
        Get detailed level info for a user.
        """
        xp = self.get_xp(user_id)
        level = 1 + xp // XP_PER_LEVEL
        xp_for_current = (level - 1) * XP_PER_LEVEL
        xp_for_next = level * XP_PER_LEVEL
        progress_xp = xp - xp_for_current
        total_for_level = xp_for_next - xp_for_current

        return {
            'level': level,
            'xp': xp,
            'xp_in_level': progress_xp,
            'xp_for_level': total_for_level,
            'xp_to_next': xp_for_next - xp,
            'progress_percent': round(progress_xp / total_for_level * 100, 1) if total_for_level else 100,
        }

    def get_badges(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Evaluate all badge conditions and return list of earned badges.
        No storage — computed each time. Includes progress for context.
        """
        stats = self._get_user_stats(user_id)
        earned = []

        for badge in BADGE_DEFINITIONS:
            try:
                if badge['condition'](stats):
                    # Include progress (100% since earned)
                    progress_key = badge.get('progress_key')
                    progress_target = badge.get('progress_target', 1)
                    current = stats.get(progress_key, 0) if progress_key else 0

                    earned.append({
                        'id': badge['id'],
                        'name': badge['name'],
                        'description': badge['description'],
                        'icon': badge['icon'],
                        'progress': {
                            'current': current,
                            'target': progress_target,
                            'percent': 100.0,
                        },
                    })
            except Exception as e:
                self.logger.warning(f"Badge {badge['id']} condition error: {e}")

        self.logger.debug(f"User {user_id} earned {len(earned)} badges")
        return earned

    def get_all_badges(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Return all badges (earned and not earned) with status and progress.
        """
        stats = self._get_user_stats(user_id)
        result = []

        for badge in BADGE_DEFINITIONS:
            try:
                earned = badge['condition'](stats)
            except Exception:
                earned = False

            # Compute progress toward badge
            progress_key = badge.get('progress_key')
            progress_target = badge.get('progress_target', 1)
            current = stats.get(progress_key, 0) if progress_key else 0
            percent = min(100.0, round(current / progress_target * 100, 1)) if progress_target else (100.0 if earned else 0.0)

            result.append({
                'id': badge['id'],
                'name': badge['name'],
                'description': badge['description'],
                'icon': badge['icon'],
                'earned': earned,
                'progress': {
                    'current': current,
                    'target': progress_target,
                    'percent': percent,
                },
            })

        return result

    def get_user_gamification(self, user_id: int) -> Dict[str, Any]:
        """
        Get full gamification summary for a user.
        """
        return {
            'user_id': user_id,
            'xp': self.get_xp(user_id),
            'level': self.get_level(user_id),
            'level_progress': self.get_level_progress(user_id),
            'badges': self.get_badges(user_id),
            'badge_count': len(self.get_badges(user_id)),
            'badge_total': len(BADGE_DEFINITIONS),
        }
