"""
Permissions - Role-based access control for n-layered architecture.
"""

from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """
    Permission class for Admin role only.
    """
    message = "Only administrators have access to this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsContentCreator(BasePermission):
    """
    Permission class for Content Creator role only.
    """
    message = "Only content creators have access to this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_content_creator

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsRegularUser(BasePermission):
    """
    Permission class for regular users.
    """
    message = "Only regular users have access to this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_regular_user

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrContentCreator(BasePermission):
    """
    Permission class for Admin or Content Creator roles.
    """
    message = "Only administrators and content creators have access to this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.can_manage_content()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsAdminOrSelf(BasePermission):
    """
    Permission class for Admin or the user themselves.
    """
    message = "Only administrators or the user themselves have access to this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin:
            return True
        # Check if obj is a user or has a user attribute
        if hasattr(obj, 'id') and obj.id == request.user.id:
            return True
        if hasattr(obj, 'user') and obj.user.id == request.user.id:
            return True
        return False


class IsPremiumUser(BasePermission):
    """
    Permission class for premium users only.
    """
    message = "Only premium users have access to this resource."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        # Check subscription
        if hasattr(request.user, 'subscription'):
            return request.user.subscription.is_premium
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
