"""
User repository - Data access layer for users.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from django.db.models import Q
from app.models.models import CustomUser, UserRole
from app.core.logger import get_logger


logger = get_logger(__name__)


class UserRepository:
    """
    Repository class for User data access operations.
    Handles all database operations for users.
    """

    @staticmethod
    def get_by_id(user_id: int) -> Optional[CustomUser]:
        """Get a user by ID."""
        logger.debug(f"get_by_id called with user_id={user_id}")
        try:
            user = CustomUser.objects.get(id=user_id, is_active=True)
            logger.debug(f"User {user_id} retrieved: {user.email}")
            return user
        except CustomUser.DoesNotExist:
            logger.debug(f"User {user_id} not found")
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[CustomUser]:
        """Get a user by email."""
        logger.debug(f"get_by_email called with email={email}")
        try:
            user = CustomUser.objects.get(email=email)
            logger.debug(f"User with email {email} found: ID={user.id}")
            return user
        except CustomUser.DoesNotExist:
            logger.debug(f"User with email {email} not found")
            return None

    @staticmethod
    def get_all() -> List[CustomUser]:
        """Get all active users."""
        logger.debug("get_all called")
        users = list(CustomUser.objects.filter(is_active=True))
        logger.debug(f"Retrieved {len(users)} active users")
        return users

    @staticmethod
    def get_by_role(role: str) -> List[CustomUser]:
        """Get users by role."""
        logger.debug(f"get_by_role called with role={role}")
        users = list(CustomUser.objects.filter(role=role, is_active=True))
        logger.debug(f"Retrieved {len(users)} users with role {role}")
        return users

    @staticmethod
    def get_admins() -> List[CustomUser]:
        """Get all admin users."""
        logger.debug("get_admins called")
        users = list(CustomUser.objects.filter(role=UserRole.ADMIN, is_active=True))
        logger.debug(f"Retrieved {len(users)} admin users")
        return users

    @staticmethod
    def get_content_creators() -> List[CustomUser]:
        """Get all content creator users."""
        logger.debug("get_content_creators called")
        users = list(CustomUser.objects.filter(role=UserRole.CONTENT_CREATOR, is_active=True))
        logger.debug(f"Retrieved {len(users)} content creator users")
        return users

    @staticmethod
    def get_regular_users() -> List[CustomUser]:
        """Get all regular users."""
        logger.debug("get_regular_users called")
        users = list(CustomUser.objects.filter(role=UserRole.USER, is_active=True))
        logger.debug(f"Retrieved {len(users)} regular users")
        return users

    @staticmethod
    def create(**kwargs) -> CustomUser:
        """Create a new user."""
        logger.info(f"Creating user with email={kwargs.get('email', 'unknown')}")
        user = CustomUser.objects.create_user(**kwargs)
        logger.info(f"User created: ID={user.id}, email={user.email}")
        return user

    @staticmethod
    def update(user: CustomUser, **kwargs) -> CustomUser:
        """Update a user."""
        logger.debug(f"Updating user {user.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'password']:
                setattr(user, key, value)
        user.save()
        logger.debug(f"User {user.id} updated successfully")
        return user

    @staticmethod
    def update_password(user: CustomUser, password: str) -> CustomUser:
        """Update user password."""
        logger.debug(f"Updating password for user {user.id}")
        user.set_password(password)
        user.save()
        logger.info(f"Password updated for user {user.id}")
        return user

    @staticmethod
    def delete(user: CustomUser) -> None:
        """Soft delete a user."""
        logger.info(f"Soft deleting user {user.id}")
        user.soft_delete()
        logger.info(f"User {user.id} soft deleted")

    @staticmethod
    def search(query: str) -> List[CustomUser]:
        """Search users by email, first name, or last name."""
        logger.debug(f"search called with query={query}")
        users = list(CustomUser.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            is_active=True
        ))
        logger.debug(f"Search found {len(users)} users for query '{query}'")
        return users

    @staticmethod
    def count() -> int:
        """Get total count of active users."""
        logger.debug("count called")
        count = CustomUser.objects.filter(is_active=True).count()
        logger.debug(f"Total active users: {count}")
        return count

    @staticmethod
    def count_by_role(role: str) -> int:
        """Get count of users by role."""
        logger.debug(f"count_by_role called with role={role}")
        count = CustomUser.objects.filter(role=role, is_active=True).count()
        logger.debug(f"Users with role {role}: {count}")
        return count
