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


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT login view with user info."""
    serializer_class = CustomTokenObtainPairSerializer

    @swagger_auto_schema(tags=['Authentication'])
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class UserRegistrationView(APIView):
    """View for user registration."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(tags=['Authentication'])
    def post(self, request):
        service = UserService()
        serializer = UserRegistrationSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                user = service.create_user(**serializer.validated_data)
                response_serializer = UserSerializer(user)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(APIView):
    """View for user profile operations."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Users'])
    def put(self, request):
        service = UserService()
        serializer = UserUpdateSerializer(data=request.data)
        
        if serializer.is_valid():
            user = service.update_user(request.user.id, **serializer.validated_data)
            response_serializer = UserSerializer(user)
            return Response(response_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """View for listing users (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request):
        service = UserService()
        role = request.query_params.get('role')
        users = service.list_users(role=role)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class UserDetailView(APIView):
    """View for user detail operations (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request, user_id):
        service = UserService()
        try:
            user = service.get_user(user_id)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(tags=['Users'])
    def delete(self, request, user_id):
        service = UserService()
        try:
            service.delete_user(user_id)
            return Response({'message': 'User deleted'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserStatsView(APIView):
    """View for user statistics (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def get(self, request):
        service = UserService()
        stats = service.get_user_stats()
        serializer = UserStatsSerializer(stats)
        return Response(serializer.data)


class ChangePasswordView(APIView):
    """View for changing password."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Users'])
    def post(self, request):
        service = UserService()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                service.change_password(
                    request.user.id,
                    serializer.validated_data['old_password'],
                    serializer.validated_data['new_password']
                )
                return Response({'message': 'Password changed'}, status=status.HTTP_200_OK)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserRoleManagementView(APIView):
    """View for managing user roles (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Users'])
    def post(self, request, user_id, action):
        service = UserService()
        try:
            if action == 'promote-content-creator':
                user = service.promote_to_content_creator(user_id)
            elif action == 'promote-admin':
                user = service.promote_to_admin(user_id)
            elif action == 'demote-user':
                user = service.demote_to_user(user_id)
            else:
                return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
