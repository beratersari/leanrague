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
from app.core.logger import get_logger


class UserService:
    """
    Service class for User business logic operations.
    Contains all business rules and logic for user management.
    """

    def __init__(self):
        self.repository = UserRepository()
        self.logger = get_logger(__name__)

    def get_user(self, user_id: int) -> CustomUser:
        """Get a user by ID."""
        self.logger.debug(f"get_user called with user_id={user_id}")
        user = self.repository.get_by_id(user_id)
        if not user:
            self.logger.warning(f"User with ID {user_id} not found")
            raise UserNotFoundException(f"User with ID {user_id} not found")
        self.logger.debug(f"User with ID {user_id} found: {user.email}")
        return user

    def get_user_by_email(self, email: str) -> CustomUser:
        """Get a user by email."""
        self.logger.debug(f"get_user_by_email called with email={email}")
        user = self.repository.get_by_email(email)
        if not user:
            self.logger.warning(f"User with email {email} not found")
            raise UserNotFoundException(f"User with email {email} not found")
        self.logger.debug(f"User with email {email} found: ID={user.id}")
        return user

    def list_users(self, role: Optional[str] = None) -> List[CustomUser]:
        """List all users, optionally filtered by role."""
        self.logger.debug(f"list_users called with role={role}")
        if role:
            if role not in [UserRole.ADMIN, UserRole.CONTENT_CREATOR, UserRole.USER]:
                self.logger.error(f"Invalid role provided: {role}")
                raise ValidationException(f"Invalid role: {role}")
            users = self.repository.get_by_role(role)
            self.logger.info(f"Listed {len(users)} users with role {role}")
            return users
        users = self.repository.get_all()
        self.logger.info(f"Listed all users: {len(users)} total")
        return users

    def create_user(self, email: str, password: str, **kwargs) -> CustomUser:
        """Create a new user."""
        self.logger.info(f"Creating user with email={email}")
        existing_user = self.repository.get_by_email(email)
        if existing_user:
            self.logger.warning(f"User creation failed: email {email} already exists")
            raise UserAlreadyExistsException(f"User with email {email} already exists")

        role = kwargs.get('role', UserRole.USER)
        if role not in [UserRole.ADMIN, UserRole.CONTENT_CREATOR, UserRole.USER]:
            self.logger.error(f"User creation failed: invalid role {role}")
            raise ValidationException(f"Invalid role: {role}")

        user = self.repository.create(
            email=email,
            password=password,
            role=role,
            first_name=kwargs.get('first_name', ''),
            last_name=kwargs.get('last_name', ''),
            phone_number=kwargs.get('phone_number'),
        )
        self.logger.info(f"User created successfully: ID={user.id}, email={email}, role={role}")
        return user

    def update_user(self, user_id: int, **kwargs) -> CustomUser:
        """Update a user."""
        self.logger.info(f"Updating user ID={user_id} with kwargs={kwargs}")
        user = self.get_user(user_id)

        if 'role' in kwargs:
            if kwargs['role'] not in [UserRole.ADMIN, UserRole.CONTENT_CREATOR, UserRole.USER]:
                self.logger.error(f"Update failed: invalid role {kwargs['role']}")
                raise ValidationException(f"Invalid role: {kwargs['role']}")

        if 'email' in kwargs and kwargs['email'] != user.email:
            existing = self.repository.get_by_email(kwargs['email'])
            if existing:
                self.logger.warning(f"Update failed: email {kwargs['email']} already in use")
                raise UserAlreadyExistsException(f"Email {kwargs['email']} already in use")

        updated_user = self.repository.update(user, **kwargs)
        self.logger.info(f"User ID={user_id} updated successfully")
        return updated_user

    def change_password(self, user_id: int, old_password: str, new_password: str) -> CustomUser:
        """Change user password."""
        self.logger.info(f"Changing password for user ID={user_id}")
        user = self.get_user(user_id)

        if not user.check_password(old_password):
            self.logger.warning(f"Password change failed for user ID={user_id}: incorrect current password")
            raise ValidationException("Current password is incorrect")

        if len(new_password) < 8:
            self.logger.warning(f"Password change failed for user ID={user_id}: password too short")
            raise ValidationException("New password must be at least 8 characters")

        updated_user = self.repository.update_password(user, new_password)
        self.logger.info(f"Password changed successfully for user ID={user_id}")
        return updated_user

    def delete_user(self, user_id: int) -> None:
        """Delete a user (soft delete)."""
        self.logger.info(f"Deleting user ID={user_id}")
        user = self.get_user(user_id)
        self.repository.delete(user)
        self.logger.info(f"User ID={user_id} deleted successfully")

    def search_users(self, query: str) -> List[CustomUser]:
        """Search users."""
        self.logger.debug(f"search_users called with query={query}")
        if not query or len(query) < 2:
            self.logger.error(f"Search failed: query too short ({len(query) if query else 0} chars)")
            raise ValidationException("Search query must be at least 2 characters")
        results = self.repository.search(query)
        self.logger.info(f"Search found {len(results)} users for query '{query}'")
        return results

    def get_user_stats(self) -> dict:
        """Get user statistics."""
        self.logger.debug("get_user_stats called")
        stats = {
            'total_users': self.repository.count(),
            'admins': self.repository.count_by_role(UserRole.ADMIN),
            'content_creators': self.repository.count_by_role(UserRole.CONTENT_CREATOR),
            'regular_users': self.repository.count_by_role(UserRole.USER),
        }
        self.logger.info(f"User stats: {stats}")
        return stats

    def promote_to_content_creator(self, user_id: int) -> CustomUser:
        """Promote a user to content creator (Admin only)."""
        self.logger.info(f"Promoting user ID={user_id} to content creator")
        user = self.get_user(user_id)
        updated_user = self.repository.update(user, role=UserRole.CONTENT_CREATOR)
        self.logger.info(f"User ID={user_id} promoted to content creator")
        return updated_user

    def promote_to_admin(self, user_id: int) -> CustomUser:
        """Promote a user to admin (Admin only)."""
        self.logger.info(f"Promoting user ID={user_id} to admin")
        user = self.get_user(user_id)
        updated_user = self.repository.update(user, role=UserRole.ADMIN)
        self.logger.info(f"User ID={user_id} promoted to admin")
        return updated_user

    def demote_to_user(self, user_id: int) -> CustomUser:
        """Demote a user to regular user (Admin only)."""
        self.logger.info(f"Demoting user ID={user_id} to regular user")
        user = self.get_user(user_id)
        updated_user = self.repository.update(user, role=UserRole.USER)
        self.logger.info(f"User ID={user_id} demoted to regular user")
        return updated_user
