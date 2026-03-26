"""
User views.
N-layered architecture: View layer.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.api.serializers.user_serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    UserUpdateSerializer,
    AdminUserUpdateSerializer,
    ChangePasswordSerializer,
    UserStatsSerializer,
    CustomTokenObtainPairSerializer,
)
from app.services.user_service import UserService
from app.permissions.role_permissions import IsAdmin
from app.core.logger import get_logger


logger = get_logger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view with user info."""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(tags=['Authentication'])
    def post(self, request, *args, **kwargs):
        logger.info(f"Login attempt with username={request.data.get('username', request.data.get('email', 'unknown'))}")
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(f"Login successful")
        else:
            logger.warning(f"Login failed with status {response.status_code}")
        return response


class UserRegistrationView(APIView):
    """View for user registration."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Authentication'])
    def post(self, request):
        logger.info(f"Registration attempt with email={request.data.get('email', 'unknown')}")
        service = UserService()
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = service.create_user(**serializer.validated_data)
                logger.info(f"Registration successful: user_id={user.id}, email={user.email}")
                response_serializer = UserSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                logger.error(f"Registration failed: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.warning(f"Registration validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """View for user profile operations."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request):
        logger.debug(f"Profile view for user_id={request.user.id}, email={request.user.email}")
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Users'])
    def put(self, request):
        logger.info(f"Profile update for user_id={request.user.id}, email={request.user.email}")
        service = UserService()
        serializer = UserUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            user = service.update_user(request.user.id, **serializer.validated_data)
            logger.info(f"Profile updated for user_id={request.user.id}, email={request.user.email}")
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data)
        
        logger.warning(f"Profile update validation failed for user_id={request.user.id}, email={request.user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """View for listing users (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request):
        role = request.query_params.get('role')
        logger.info(f"Admin listing users (role filter: {role})")
        service = UserService()
        users = service.list_users(role=role)
        logger.debug(f"Listed {len(users)} users")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """View for user detail operations (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, user_id):
        logger.info(f"UserDetailView.get: admin_id={request.user.id}, admin_email={request.user.email}, target_user_id={user_id}")
        service = UserService()
        try:
            user = service.get_user(user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"UserDetailView.get: user {user_id} not found - {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(tags=['Users'])
    def delete(self, request, user_id):
        logger.info(f"UserDetailView.delete: admin_id={request.user.id}, admin_email={request.user.email}, target_user_id={user_id}")
        service = UserService()
        try:
            service.delete_user(user_id)
            logger.info(f"UserDetailView.delete: user {user_id} deleted")
            return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.error(f"UserDetailView.delete: failed to delete user {user_id} - {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """View for user statistics (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request):
        logger.info(f"UserStatsView.get: admin_id={request.user.id}, admin_email={request.user.email}")
        service = UserService()
        stats = service.get_user_stats()
        logger.debug(f"UserStatsView.get: stats={stats}")
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """View for changing password."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def post(self, request):
        logger.info(f"Password change request for user_id={request.user.id}, email={request.user.email}")
        service = UserService()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service.change_password(
                    request.user.id,
                    serializer.validated_data['old_password'],
                    serializer.validated_data['new_password']
                )
                logger.info(f"Password changed successfully for user_id={request.user.id}, email={request.user.email}")
                return Response({'message': 'Password changed'}, status=status.HTTP_200_OK)
            except Exception as e:
                logger.warning(f"Password change failed for user_id={request.user.id}, email={request.user.email}: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.warning(f"Password change validation failed for user_id={request.user.id}, email={request.user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleManagementView(APIView):
    """View for managing user roles (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def post(self, request, user_id, action):
        logger.info(f"Role management: admin_id={request.user.id}, admin_email={request.user.email}, action={action}, target_user_id={user_id}")
        service = UserService()
        try:
            if action == 'promote-content-creator':
                user = service.promote_to_content_creator(user_id)
            elif action == 'promote-admin':
                user = service.promote_to_admin(user_id)
            elif action == 'demote-user':
                user = service.demote_to_user(user_id)
            else:
                logger.warning(f"Invalid role management action: {action} by admin_id={request.user.id}")
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            logger.info(f"Role management success: admin_id={request.user.id}, action={action}, target_user_id={user_id}, target_email={user.email}")
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Role management failed: admin_id={request.user.id}, action={action}, target_user_id={user_id}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# =============================================================================
# FOLLOW VIEWS - User Following System
# =============================================================================

class FollowUserView(APIView):
    """Follow a user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def post(self, request, user_id):
        logger.info(f"FollowUserView: user_id={request.user.id} follows {user_id}")
        from app.services.follow_service import FollowService
        service = FollowService()
        result = service.follow(request.user, user_id)
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class UnfollowUserView(APIView):
    """Unfollow a user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def post(self, request, user_id):
        logger.info(f"UnfollowUserView: user_id={request.user.id} unfollows {user_id}")
        from app.services.follow_service import FollowService
        service = FollowService()
        result = service.unfollow(request.user, user_id)
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        return Response(result, status=status.HTTP_400_BAD_REQUEST)


class UserFollowersView(APIView):
    """List followers of a user."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, user_id):
        logger.debug(f"UserFollowersView: get followers of user {user_id}")
        from app.services.follow_service import FollowService
        from app.api.serializers.user_serializers import UserSerializer
        service = FollowService()
        followers = service.get_followers(user_id)
        serializer = UserSerializer(followers, many=True)
        return Response({
            'count': len(followers),
            'followers': serializer.data,
        })


class UserFollowingView(APIView):
    """List users that a user is following."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, user_id):
        logger.debug(f"UserFollowingView: get following of user {user_id}")
        from app.services.follow_service import FollowService
        from app.api.serializers.user_serializers import UserSerializer
        service = FollowService()
        following = service.get_following(user_id)
        serializer = UserSerializer(following, many=True)
        return Response({
            'count': len(following),
            'following': serializer.data,
        })
