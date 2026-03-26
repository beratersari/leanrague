"""
Custom JWT Authentication that handles tokens with or without 'Bearer' prefix.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser
from app.core.logger import get_logger


logger = get_logger(__name__)


class FlexibleJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication that accepts tokens with or without 'Bearer' prefix.
    
    Supports:
    - "Bearer <token>" (standard format)
    - "<token>" (token only, no prefix)
    """

    def authenticate(self, request):
        """
        Authenticate the request and return a two-tuple of (user, token).
        """
        logger.debug("FlexibleJWTAuthentication.authenticate called")
        header = self.get_header(request)
        
        if header is None:
            logger.debug("No authorization header found")
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            logger.debug("No raw token extracted from header")
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)
            logger.info(f"JWT authentication successful for user_id={user.id}, email={user.email}")
            return user, validated_token
        except TokenError as e:
            logger.warning(f"JWT authentication failed: {e}")
            raise InvalidToken(str(e))

    def get_header(self, request):
        """
        Extract the Authorization header from the request.
        """
        logger.debug("get_header called")
        header = super().get_header(request)
        if header:
            logger.debug(f"get_header: found authorization header")
        else:
            logger.debug("get_header: no authorization header")
        return header

    def get_raw_token(self, header):
        """
        Extract the raw token from the Authorization header.
        Handles both "Bearer <token>" and "<token>" formats.
        """
        logger.debug(f"get_raw_token called with header: {header[:50]}...")
        parts = header.split()
        
        if len(parts) == 0:
            logger.debug("get_raw_token: no parts in header")
            return None
        
        # If only one part, treat it as the token directly
        if len(parts) == 1:
            logger.debug("get_raw_token: single part token")
            return parts[0]
        
        # If two parts, check if first is "Bearer" or "Token"
        if len(parts) == 2:
            auth_type = parts[0].lower()
            if auth_type in ('bearer', 'token'):
                logger.debug(f"get_raw_token: found {auth_type} prefix")
                return parts[1]
            # If not a known prefix, try the whole thing as token
            logger.debug("get_raw_token: no known prefix, treating whole header as token")
            return header
        
        # If more than 2 parts, join everything after first as token
        if parts[0].lower() in ('bearer', 'token'):
            return b' '.join(parts[1:])
        
        # Fallback: treat entire header as token
        return header

    def get_validated_token(self, raw_token):
        """
        Validate the token and return the validated token.
        """
        logger.debug("get_validated_token called")
        try:
            validated = super().get_validated_token(raw_token)
            logger.debug("get_validated_token: token validated successfully")
            return validated
        except Exception as e:
            logger.warning(f"get_validated_token: validation failed - {e}")
            raise

    def get_user(self, validated_token):
        """
        Get the user from the validated token.
        """
        logger.debug("get_user called")
        user = super().get_user(validated_token)
        logger.debug(f"get_user: retrieved user_id={user.id}")
        return user

    def authenticate_header(self, request):
        """
        Return the WWW-Authenticate header value.
        """
        logger.debug("authenticate_header called")
        return super().authenticate_header(request)
