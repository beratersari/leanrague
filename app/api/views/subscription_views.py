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
from app.core.logger import get_logger


logger = get_logger(__name__)


class UserSubscriptionView(APIView):
    """View for user's own subscription."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        logger.debug(f"Subscription view for user_id={request.user.id}, email={request.user.email}")
        service = SubscriptionService()
        subscription = service.get_user_subscription(request.user.id)
        serializer = SubscriptionSerializer(subscription)
        return Response(serializer.data)

    @swagger_auto_schema(tags=['Subscriptions'])
    def post(self, request):
        logger.info(f"Subscription upgrade request for user_id={request.user.id}, email={request.user.email}")
        service = SubscriptionService()
        serializer = SubscriptionUpgradeSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                subscription = service.upgrade_subscription(request.user.id, **serializer.validated_data)
                logger.info(f"Subscription upgraded for user_id={request.user.id}, email={request.user.email}, new_plan={subscription.plan}")
                response_serializer = SubscriptionSerializer(subscription)
                return Response(response_serializer.data)
            except Exception as e:
                logger.warning(f"Subscription upgrade failed for user_id={request.user.id}, email={request.user.email}: {e}")
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.warning(f"Subscription upgrade validation failed for user_id={request.user.id}, email={request.user.email}: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionCancelView(APIView):
    """View for cancelling subscription."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Subscriptions'])
    def post(self, request):
        logger.info(f"Subscription cancel request for user_id={request.user.id}, email={request.user.email}")
        service = SubscriptionService()
        try:
            subscription = service.cancel_subscription(request.user.id)
            logger.info(f"Subscription cancelled for user_id={request.user.id}, email={request.user.email}")
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"Subscription cancel failed for user_id={request.user.id}, email={request.user.email}: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SubscriptionCheckPremiumView(APIView):
    """View for checking premium access."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        logger.debug(f"SubscriptionCheckPremiumView.get: user_id={request.user.id}, email={request.user.email}")
        service = SubscriptionService()
        has_access = service.check_premium_access(request.user.id)
        logger.debug(f"SubscriptionCheckPremiumView.get: has_premium_access={has_access}")
        return Response({'has_premium_access': has_access})


class AdminSubscriptionListView(APIView):
    """View for listing all subscriptions (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        logger.info(f"AdminSubscriptionListView.get: admin_id={request.user.id}, admin_email={request.user.email}")
        service = SubscriptionService()
        plan = request.query_params.get('plan')
        status = request.query_params.get('status')
        subscriptions = service.list_subscriptions(plan=plan, status=status)
        logger.debug(f"AdminSubscriptionListView.get: returning {len(subscriptions)} subscriptions")
        serializer = SubscriptionSerializer(subscriptions, many=True)
        return Response(serializer.data)


class AdminSubscriptionDetailView(APIView):
    """View for subscription detail operations (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request, subscription_id):
        logger.info(f"AdminSubscriptionDetailView.get: admin_id={request.user.id}, admin_email={request.user.email}, subscription_id={subscription_id}")
        service = SubscriptionService()
        try:
            subscription = service.get_subscription(subscription_id)
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        except Exception as e:
            logger.warning(f"AdminSubscriptionDetailView.get: subscription {subscription_id} not found - {e}")
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


class AdminPremiumUsersView(APIView):
    """View for listing premium users (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        logger.info(f"AdminPremiumUsersView.get: admin_id={request.user.id}, admin_email={request.user.email}")
        service = SubscriptionService()
        subscriptions = service.get_premium_users()
        logger.debug(f"AdminPremiumUsersView.get: returning {len(subscriptions)} premium users")
        serializer = PremiumUserSerializer(subscriptions, many=True)
        return Response(serializer.data)


class AdminSubscriptionStatsView(APIView):
    """View for subscription statistics (Admin only)."""
    permission_classes = [IsAuthenticated, IsAdmin]

    @swagger_auto_schema(tags=['Subscriptions'])
    def get(self, request):
        logger.info(f"AdminSubscriptionStatsView.get: admin_id={request.user.id}, admin_email={request.user.email}")
        service = SubscriptionService()
        stats = service.get_subscription_stats()
        logger.debug(f"AdminSubscriptionStatsView.get: stats={stats}")
        serializer = SubscriptionStatsSerializer(stats)
        return Response(serializer.data)
