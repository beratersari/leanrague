"""
Custom JWT Authentication that handles tokens with or without 'Bearer' prefix.
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth.models import AnonymousUser


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
        header = self.get_header(request)
        
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
        except TokenError as e:
            raise InvalidToken(str(e))

        return self.get_user(validated_token), validated_token

    def get_raw_token(self, header):
        """
        Extract the raw token from the Authorization header.
        Handles both "Bearer <token>" and "<token>" formats.
        """
        parts = header.split()
        
        if len(parts) == 0:
            return None
        
        # If only one part, treat it as the token directly
        if len(parts) == 1:
            return parts[0]
        
        # If two parts, check if first is "Bearer" or "Token"
        if len(parts) == 2:
            auth_type = parts[0].lower()
            if auth_type in ('bearer', 'token'):
                return parts[1]
            # If not a known prefix, try the whole thing as token
            return header
        
        # If more than 2 parts, join everything after first as token
        if parts[0].lower() in ('bearer', 'token'):
            return b' '.join(parts[1:])
        
        # Fallback: treat entire header as token
        return header
