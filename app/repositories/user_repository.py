"""
User repository - Data access layer for users.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from django.db.models import Q
from app.models.models import CustomUser, UserRole


class UserRepository:
    """
    Repository class for User data access operations.
    Handles all database operations for users.
    """

    @staticmethod
    def get_by_id(user_id: int) -> Optional[CustomUser]:
        """Get a user by ID."""
        try:
            return CustomUser.objects.get(id=user_id, is_active=True)
        except CustomUser.DoesNotExist:
            return None

    @staticmethod
    def get_by_email(email: str) -> Optional[CustomUser]:
        """Get a user by email."""
        try:
            return CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[CustomUser]:
        """Get all active users."""
        return list(CustomUser.objects.filter(is_active=True))

    @staticmethod
    def get_by_role(role: str) -> List[CustomUser]:
        """Get users by role."""
        return list(CustomUser.objects.filter(role=role, is_active=True))

    @staticmethod
    def get_admins() -> List[CustomUser]:
        """Get all admin users."""
        return list(CustomUser.objects.filter(role=UserRole.ADMIN, is_active=True))

    @staticmethod
    def get_content_creators() -> List[CustomUser]:
        """Get all content creator users."""
        return list(CustomUser.objects.filter(role=UserRole.CONTENT_CREATOR, is_active=True))

    @staticmethod
    def get_regular_users() -> List[CustomUser]:
        """Get all regular users."""
        return list(CustomUser.objects.filter(role=UserRole.USER, is_active=True))

    @staticmethod
    def create(**kwargs) -> CustomUser:
        """Create a new user."""
        return CustomUser.objects.create_user(**kwargs)

    @staticmethod
    def update(user: CustomUser, **kwargs) -> CustomUser:
        """Update a user."""
        for key, value in kwargs.items():
            if hasattr(user, key) and key not in ['id', 'password']:
                setattr(user, key, value)
        user.save()
        return user

    @staticmethod
    def update_password(user: CustomUser, password: str) -> CustomUser:
        """Update user password."""
        user.set_password(password)
        user.save()
        return user

    @staticmethod
    def delete(user: CustomUser) -> None:
        """Soft delete a user."""
        user.soft_delete()

    @staticmethod
    def search(query: str) -> List[CustomUser]:
        """Search users by email, first name, or last name."""
        return list(CustomUser.objects.filter(
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            is_active=True
        ))

    @staticmethod
    def count() -> int:
        """Get total count of active users."""
        return CustomUser.objects.filter(is_active=True).count()

    @staticmethod
    def count_by_role(role: str) -> int:
        """Get count of users by role."""
        return CustomUser.objects.filter(role=role, is_active=True).count()
