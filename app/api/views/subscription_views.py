"""
Subscription views.
N-layered architecture: View layer.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from app.api.serializers.subscription_serializers import (
    SubscriptionSerializer,
    SubscriptionUpgradeSerializer,
    SubscriptionStatsSerializer,
    PremiumUserSerializer,
)
from app.services.subscription_service import SubscriptionService
from app.permissions.role_permissions import IsAdmin


class UserSubscriptionView(APIView):
    """View for user's own subscription."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        service = SubscriptionService()
        subscription = service.get_user_subscription(request.user.id)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Subscriptions'])
    def post(self, request):
        service = SubscriptionService()
        serializer = SubscriptionUpgradeSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                subscription = service.upgrade_subscription(request.user.id, **serializer.validated_data)
                response_serializer = SubscriptionSerializer(subscription)
                return Response(response_serializer.data)
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionCancelView(APIView):
    """View for cancelling subscription."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Subscriptions'])
    def post(self, request):
        service = SubscriptionService()
        try:
            subscription = service.cancel_subscription(request.user.id)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionCheckPremiumView(APIView):
    """View for checking premium access."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        service = SubscriptionService()
        has_access = service.check_premium_access(request.user.id)
        return Response({'has_premium_access': has_access})


class AdminSubscriptionListView(APIView):
    """View for listing all subscriptions (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        service = SubscriptionService()
        plan = request.query_params.get('plan')
        status = request.query_params.get('status')
        subscriptions = service.list_subscriptions(plan=plan, status=status)
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class AdminSubscriptionDetailView(APIView):
    """View for subscription detail operations (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request, subscription_id):
        service = SubscriptionService()
        try:
            subscription = service.get_subscription(subscription_id)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class AdminPremiumUsersView(APIView):
    """View for listing premium users (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        service = SubscriptionService()
        subscriptions = service.get_premium_users()
        serializer = PremiumUserSerializer(subscriptions, many=True)
        return Response(serializer.data)


class AdminSubscriptionStatsView(APIView):
    """View for subscription statistics (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        service = SubscriptionService()
        stats = service.get_subscription_stats()
        serializer = SubscriptionStatsSerializer(stats)
        return Response(serializer.data)
