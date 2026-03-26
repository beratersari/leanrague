"""
Follow service - Business logic for user following.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from django.utils import timezone

from app.models.models import CustomUser, UserFollow
from app.core.logger import get_logger


logger = get_logger(__name__)


class FollowService:
    """Service for user following logic."""

    def follow(self, follower: CustomUser, following_id: int) -> dict:
        """
        Follow a user.
        Returns {success, message, follow?}
        """
        if follower.id == following_id:
            return {'success': False, 'error': 'Cannot follow yourself'}

        try:
            following = CustomUser.objects.get(id=following_id, is_active=True)
        except CustomUser.DoesNotExist:
            return {'success': False, 'error': 'User not found'}

        follow, created = UserFollow.objects.get_or_create(
            follower=follower,
            following=following,
        )
        if created:
            logger.info(f"User {follower.id} now follows {following_id}")
            return {'success': True, 'message': 'Followed successfully', 'follow': follow}
        else:
            return {'success': True, 'message': 'Already following', 'already': True}

    def unfollow(self, follower: CustomUser, following_id: int) -> dict:
        """Unfollow a user."""
        try:
            follow = UserFollow.objects.get(follower=follower, following_id=following_id)
            follow.delete()
            logger.info(f"User {follower.id} unfollowed {following_id}")
            return {'success': True, 'message': 'Unfollowed successfully'}
        except UserFollow.DoesNotExist:
            return {'success': False, 'error': 'Not following this user'}

    def is_following(self, follower: CustomUser, following_id: int) -> bool:
        """Check if follower follows following_id."""
        return UserFollow.objects.filter(follower=follower, following_id=following_id).exists()

    def get_followers(self, user_id: int, limit: int = 50) -> List[CustomUser]:
        """Get list of users following this user."""
        follows = UserFollow.objects.filter(following_id=user_id).select_related('follower')[:limit]
        return [f.follower for f in follows]

    def get_following(self, user_id: int, limit: int = 50) -> List[CustomUser]:
        """Get list of users this user is following."""
        follows = UserFollow.objects.filter(follower_id=user_id).select_related('following')[:limit]
        return [f.following for f in follows]

    def get_follower_count(self, user_id: int) -> int:
        """Count followers."""
        return UserFollow.objects.filter(following_id=user_id).count()

    def get_following_count(self, user_id: int) -> int:
        """Count following."""
        return UserFollow.objects.filter(follower_id=user_id).count()

    def get_follow_status(self, viewer: CustomUser, target_id: int) -> dict:
        """
        Get follow status for a target user from viewer's perspective.
        Returns {followers_count, following_count, is_following}
        """
        followers_count = self.get_follower_count(target_id)
        following_count = self.get_following_count(target_id)
        is_following = self.is_following(viewer, target_id) if viewer.id != target_id else False

        return {
            'followers_count': followers_count,
            'following_count': following_count,
            'is_following': is_following,
        }
