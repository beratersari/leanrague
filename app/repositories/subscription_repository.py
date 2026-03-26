"""
Subscription repository - Data access layer for subscriptions.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from django.utils import timezone
from app.models.models import Subscription, SubscriptionPlan, SubscriptionStatus
from app.models.models import CustomUser
from app.core.logger import get_logger


logger = get_logger(__name__)


class SubscriptionRepository:
    """
    Repository class for Subscription data access operations.
    Handles all database operations for subscriptions.
    """

    @staticmethod
    def get_by_id(subscription_id: int) -> Optional[Subscription]:
        """Get a subscription by ID."""
        logger.debug(f"get_by_id called with subscription_id={subscription_id}")
        try:
            sub = Subscription.objects.get(id=subscription_id)
            logger.debug(f"Subscription {subscription_id} retrieved: plan={sub.plan}")
            return sub
        except Subscription.DoesNotExist:
            logger.debug(f"Subscription {subscription_id} not found")
            return None

    @staticmethod
    def get_by_user(user: CustomUser) -> Optional[Subscription]:
        """Get subscription by user."""
        logger.debug(f"get_by_user called for user {user.id}")
        try:
            sub = Subscription.objects.get(user=user)
            logger.debug(f"Subscription for user {user.id} found: plan={sub.plan}")
            return sub
        except Subscription.DoesNotExist:
            logger.debug(f"No subscription for user {user.id}")
            return None

    @staticmethod
    def get_by_user_id(user_id: int) -> Optional[Subscription]:
        """Get subscription by user ID."""
        logger.debug(f"get_by_user_id called with user_id={user_id}")
        try:
            sub = Subscription.objects.get(user_id=user_id)
            logger.debug(f"Subscription for user {user_id} found: plan={sub.plan}")
            return sub
        except Subscription.DoesNotExist:
            logger.debug(f"No subscription for user {user_id}")
            return None

    @staticmethod
    def get_all() -> List[Subscription]:
        """Get all subscriptions."""
        logger.debug("get_all called")
        subs = list(Subscription.objects.all())
        logger.debug(f"Retrieved {len(subs)} subscriptions")
        return subs

    @staticmethod
    def get_premium_users() -> List[Subscription]:
        """Get all premium users (active non-free subscriptions)."""
        logger.debug("get_premium_users called")
        subs = list(Subscription.objects.filter(
            plan__in=[SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE],
            status=SubscriptionStatus.ACTIVE
        ))
        logger.debug(f"Retrieved {len(subs)} premium users")
        return subs

    @staticmethod
    def get_by_plan(plan: str) -> List[Subscription]:
        """Get subscriptions by plan."""
        logger.debug(f"get_by_plan called with plan={plan}")
        subs = list(Subscription.objects.filter(plan=plan))
        logger.debug(f"Retrieved {len(subs)} subscriptions with plan {plan}")
        return subs

    @staticmethod
    def get_by_status(status: str) -> List[Subscription]:
        """Get subscriptions by status."""
        logger.debug(f"get_by_status called with status={status}")
        subs = list(Subscription.objects.filter(status=status))
        logger.debug(f"Retrieved {len(subs)} subscriptions with status {status}")
        return subs

    @staticmethod
    def get_active_subscriptions() -> List[Subscription]:
        """Get all active subscriptions."""
        logger.debug("get_active_subscriptions called")
        subs = list(Subscription.objects.filter(status=SubscriptionStatus.ACTIVE))
        logger.debug(f"Retrieved {len(subs)} active subscriptions")
        return subs

    @staticmethod
    def get_expired_subscriptions() -> List[Subscription]:
        """Get expired subscriptions."""
        logger.debug("get_expired_subscriptions called")
        subs = list(Subscription.objects.filter(status=SubscriptionStatus.EXPIRED))
        logger.debug(f"Retrieved {len(subs)} expired subscriptions")
        return subs

    @staticmethod
    def create(user: CustomUser, **kwargs) -> Subscription:
        """Create a new subscription for a user."""
        logger.info(f"Creating subscription for user {user.id} with plan={kwargs.get('plan', 'unknown')}")
        sub = Subscription.objects.create(user=user, **kwargs)
        logger.info(f"Subscription created: ID={sub.id}, plan={sub.plan}")
        return sub

    @staticmethod
    def update(subscription: Subscription, **kwargs) -> Subscription:
        """Update a subscription."""
        logger.debug(f"Updating subscription {subscription.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(subscription, key) and key not in ['id', 'user']:
                setattr(subscription, key, value)
        subscription.save()
        logger.debug(f"Subscription {subscription.id} updated successfully")
        return subscription

    @staticmethod
    def delete(subscription: Subscription) -> None:
        """Delete a subscription."""
        logger.info(f"Deleting subscription {subscription.id}")
        subscription.delete()
        logger.info(f"Subscription {subscription.id} deleted")

    @staticmethod
    def get_premium_count() -> int:
        """Get count of premium users."""
        logger.debug("get_premium_count called")
        count = Subscription.objects.filter(
            plan__in=[SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE],
            status=SubscriptionStatus.ACTIVE
        ).count()
        logger.debug(f"Premium user count: {count}")
        return count

    @staticmethod
    def get_stats() -> dict:
        """Get subscription statistics."""
        logger.debug("get_stats called")
        stats = {
            'total_subscriptions': Subscription.objects.count(),
            'free_users': Subscription.objects.filter(plan=SubscriptionPlan.FREE).count(),
            'basic_users': Subscription.objects.filter(plan=SubscriptionPlan.BASIC, status=SubscriptionStatus.ACTIVE).count(),
            'premium_users': Subscription.objects.filter(plan=SubscriptionPlan.PREMIUM, status=SubscriptionStatus.ACTIVE).count(),
            'enterprise_users': Subscription.objects.filter(plan=SubscriptionPlan.ENTERPRISE, status=SubscriptionStatus.ACTIVE).count(),
            'active': Subscription.objects.filter(status=SubscriptionStatus.ACTIVE).count(),
            'expired': Subscription.objects.filter(status=SubscriptionStatus.EXPIRED).count(),
            'cancelled': Subscription.objects.filter(status=SubscriptionStatus.CANCELLED).count(),
        }
        logger.debug(f"Subscription stats: {stats}")
        return stats
