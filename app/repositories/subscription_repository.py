"""
Subscription repository - Data access layer for subscriptions.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from django.utils import timezone
from app.models.models import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.models import CustomUser


class SubscriptionRepository:
    """
    Repository class for Subscription data access operations.
    Handles all database operations for subscriptions.
    """

    @staticmethod
    def get_by_id(subscription_id: int) -> Optional[Subscription]:
        """Get a subscription by ID."""
        try:
            return Subscription.objects.get(id=subscription_id)
        except Subscription.DoesNotExist:
            return None

    @staticmethod
    def get_by_user(user: CustomUser) -> Optional[Subscription]:
        """Get subscription by user."""
        try:
            return Subscription.objects.get(user=user)
        except Subscription.DoesNotExist:
            return None

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Subscription]:
        """Get subscription by user ID."""
        try:
            return Subscription.objects.get(user_id=user_id)
        except Subscription.DoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[Subscription]:
        """Get all subscriptions."""
        return list(Subscription.objects.all())

    @staticmethod
    def get_premium_users() -> List[Subscription]:
        """Get all premium users (active non-free subscriptions)."""
        return list(Subscription.objects.filter(
            plan__in=[SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE],
            status=SubscriptionStatus.ACTIVE
        ))

    @staticmethod
    def get_by_plan(plan: str) -> List[Subscription]:
        """Get subscriptions by plan."""
        return list(Subscription.objects.filter(plan=plan))

    @staticmethod
    def get_by_status(status: str) -> List[Subscription]:
        """Get subscriptions by status."""
        return list(Subscription.objects.filter(status=status))

    @staticmethod
    def get_active_subscriptions() -> List[Subscription]:
        """Get all active subscriptions."""
        return list(Subscription.objects.filter(status=SubscriptionStatus.ACTIVE))

    @staticmethod
    def get_expired_subscriptions() -> List[Subscription]:
        """Get expired subscriptions."""
        return list(Subscription.objects.filter(status=SubscriptionStatus.EXPIRED))

    @staticmethod
    def create(user: CustomUser, **kwargs) -> Subscription:
        """Create a new subscription for a user."""
        return Subscription.objects.create(user=user, **kwargs)

    @staticmethod
    def update(subscription: Subscription, **kwargs) -> Subscription:
        """Update a subscription."""
        for key, value in kwargs.items():
            if hasattr(subscription, key) and key not in ['id', 'user']:
                setattr(subscription, key, value)
        subscription.save()
        return subscription

    @staticmethod
    def delete(subscription: Subscription) -> None:
        """Delete a subscription."""
        subscription.delete()

    @staticmethod
    def get_premium_count() -> int:
        """Get count of premium users."""
        return Subscription.objects.filter(
            plan__in=[SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE],
            status=SubscriptionStatus.ACTIVE
        ).count()

    @staticmethod
    def get_stats() -> dict:
        """Get subscription statistics."""
        return {
            'total_subscriptions': Subscription.objects.count(),
            'free_users': Subscription.objects.filter(plan=SubscriptionPlan.FREE).count(),
            'basic_users': Subscription.objects.filter(plan=SubscriptionPlan.BASIC, status=SubscriptionStatus.ACTIVE).count(),
            'premium_users': Subscription.objects.filter(plan=SubscriptionPlan.PREMIUM, status=SubscriptionStatus.ACTIVE).count(),
            'enterprise_users': Subscription.objects.filter(plan=SubscriptionPlan.ENTERPRISE, status=SubscriptionStatus.ACTIVE).count(),
            'active': Subscription.objects.filter(status=SubscriptionStatus.ACTIVE).count(),
            'expired': Subscription.objects.filter(status=SubscriptionStatus.EXPIRED).count(),
            'cancelled': Subscription.objects.filter(status=SubscriptionStatus.CANCELLED).count(),
        }
