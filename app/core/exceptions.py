"""
Core exceptions - Custom exception classes for n-layered architecture.
"""


class BaseServiceException(Exception):
    """Base exception for service layer."""
    message = "An error occurred"
    code = "error"

    def __init__(self, message=None, code=None):
        if message:
            self.message = message
        if code:
            self.code = code
        super().__init__(self.message)


class UserNotFoundException(BaseServiceException):
    """Raised when a user is not found."""
    message = "User not found"
    code = "user_not_found"


class UserAlreadyExistsException(BaseServiceException):
    """Raised when a user already exists."""
    message = "User already exists"
    code = "user_already_exists"


class InvalidCredentialsException(BaseServiceException):
    """Raised when credentials are invalid."""
    message = "Invalid credentials"
    code = "invalid_credentials"


class SubscriptionNotFoundException(BaseServiceException):
    """Raised when a subscription is not found."""
    message = "Subscription not found"
    code = "subscription_not_found"


class PermissionDeniedException(BaseServiceException):
    """Raised when user doesn't have permission."""
    message = "Permission denied"
    code = "permission_denied"


class ValidationException(BaseServiceException):
    """Raised when validation fails."""
    message = "Validation failed"
    code = "validation_error"
