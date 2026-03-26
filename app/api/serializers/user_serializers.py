"""
User serializers.
N-layered architecture: Serializer layer.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from app.models.models import CustomUser, UserRole


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name', 'phone_number']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = CustomUser.objects.create_user(**validated_data)
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with user info."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
            'role_display': user.get_role_display(),
            'is_verified': user.is_verified,
        }
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user data (read)."""
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    full_name = serializers.CharField(read_only=True)
    followers_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = [
            'id', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'role_display', 'phone_number', 'profile_image',
            'is_verified', 'is_active', 'created_at', 'updated_at',
            'last_login_at', 'followers_count', 'following_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'last_login_at']

    def get_followers_count(self, obj):
        from app.models.models import UserFollow
        return UserFollow.objects.filter(following=obj).count()

    def get_following_count(self, obj):
        from app.models.models import UserFollow
        return UserFollow.objects.filter(follower=obj).count()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user updates."""
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'phone_number', 'profile_image']


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin user updates (includes role)."""
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'profile_image',
            'role', 'is_verified', 'is_active'
        ]


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password_confirm']:
            raise serializers.ValidationError("New passwords do not match")
        return data


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    total_users = serializers.IntegerField()
    admins = serializers.IntegerField()
    content_creators = serializers.IntegerField()
    regular_users = serializers.IntegerField()
