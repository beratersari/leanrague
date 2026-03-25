"""
User service - Business logic layer for users.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import CustomUser, UserRole
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    UserNotFoundException,
    UserAlreadyExistsException,
    ValidationException
)


class UserService:
    """
    Service class for User business logic operations.
    Contains all business rules and logic for user management.
    """

    def __init__(self):
        self.repository = UserRepository()

    def get_user(self, user_id: int) -> CustomUser:
        """Get a user by ID."""
        user = self.repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")
        return user

    def get_user_by_email(self, email: str) -> CustomUser:
        """Get a user by email."""
        user = self.repository.get_by_email(email)
        if not user:
            raise UserNotFoundException(f"User with email {email} not found")
        return user

    def list_users(self, role: Optional[str] = None) -> List[CustomUser]:
        """List all users, optionally filtered by role."""
        if role:
            if role not in [UserRole.ADMIN, UserRole.CONTENT_CREATOR, UserRole.USER]:
                raise ValidationException(f"Invalid role: {role}")
            return self.repository.get_by_role(role)
        return self.repository.get_all()

    def create_user(self, email: str, password: str, **kwargs) -> CustomUser:
        """Create a new user."""
        existing_user = self.repository.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsException(f"User with email {email} already exists")

        role = kwargs.get('role', UserRole.USER)
        if role not in [UserRole.ADMIN, UserRole.CONTENT_CREATOR, UserRole.USER]:
            raise ValidationException(f"Invalid role: {role}")

        user = self.repository.create(
            email=email,
            password=password,
            role=role,
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            phone_number=kwargs.get('phone_number'),
        )
        return user

    def update_user(self, user_id: int, **kwargs) -> CustomUser:
        """Update a user."""
        user = self.get_user(user_id)

        if 'role' in kwargs:
            if kwargs['role'] not in [UserRole.ADMIN, UserRole.CONTENT_CREATOR, UserRole.USER]:
                raise ValidationException(f"Invalid role: {kwargs['role']}")

        if 'email' in kwargs and kwargs['email'] != user.email:
            existing = self.repository.get_by_email(kwargs['email'])
            if existing:
                raise UserAlreadyExistsException(f"Email {kwargs['email']} already in use")

        return self.repository.update(user, **kwargs)

    def change_password(self, user_id: int, old_password: str, new_password: str) -> CustomUser:
        """Change user password."""
        user = self.get_user(user_id)

        if not user.check_password(old_password):
            raise ValidationException("Current password is incorrect")

        if len(new_password) < 8:
            raise ValidationException("New password must be at least 8 characters")

        return self.repository.update_password(user, new_password)

    def delete_user(self, user_id: int) -> None:
        """Delete a user (soft delete)."""
        user = self.get_user(user_id)
        self.repository.delete(user)

    def search_users(self, query: str) -> List[CustomUser]:
        """Search users."""
        if not query or len(query) < 2:
            raise ValidationException("Search query must be at least 2 characters")
        return self.repository.search(query)

    def get_user_stats(self) -> dict:
        """Get user statistics."""
        return {
            'total_users': self.repository.count(),
            'admins': self.repository.count_by_role(UserRole.ADMIN),
            'content_creators': self.repository.count_by_role(UserRole.CONTENT_CREATOR),
            'regular_users': self.repository.count_by_role(UserRole.USER),
        }

    def promote_to_content_creator(self, user_id: int) -> CustomUser:
        """Promote a user to content creator (Admin only)."""
        user = self.get_user(user_id)
        return self.repository.update(user, role=UserRole.CONTENT_CREATOR)

    def promote_to_admin(self, user_id: int) -> CustomUser:
        """Promote a user to admin (Admin only)."""
        user = self.get_user(user_id)
        return self.repository.update(user, role=UserRole.ADMIN)

    def demote_to_user(self, user_id: int) -> CustomUser:
        """Demote a user to regular user (Admin only)."""
        user = self.get_user(user_id)
        return self.repository.update(user, role=UserRole.USER)
