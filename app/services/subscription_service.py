"""
Subscription service - Business logic layer for subscriptions.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from django.utils import timezone
from datetime import timedelta
from app.models.models import Subscription, SubscriptionPlan, SubscriptionStatus
from app.repositories.subscription_repository import SubscriptionRepository
from app.repositories.user_repository import UserRepository
from app.core.exceptions import (
    SubscriptionNotFoundException,
    UserNotFoundException,
    ValidationException
)


class SubscriptionService:
    """
    Service class for Subscription business logic operations.
    Contains all business rules and logic for subscription management.
    """

    def __init__(self):
        self.repository = SubscriptionRepository()
        self.user_repository = UserRepository()

    def get_subscription(self, subscription_id: int) -> Subscription:
        """Get a subscription by ID."""
        subscription = self.repository.get_by_id(subscription_id)
        if not subscription:
            raise SubscriptionNotFoundException(f"Subscription with ID {subscription_id} not found")
        return subscription

    def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get subscription for a user, create if not exists."""
        subscription = self.repository.get_by_user_id(user_id)
        if not subscription:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                raise UserNotFoundException(f"User with ID {user_id} not found")
            subscription = self.repository.create(
                user=user,
                plan=SubscriptionPlan.FREE,
                status=SubscriptionStatus.ACTIVE
            )
        return subscription

    def list_subscriptions(self, plan: Optional[str] = None, status: Optional[str] = None) -> List[Subscription]:
        """List subscriptions with optional filters."""
        if plan:
            return self.repository.get_by_plan(plan)
        if status:
            return self.repository.get_by_status(status)
        return self.repository.get_all()

    def get_premium_users(self) -> List[Subscription]:
        """Get all premium users."""
        return self.repository.get_premium_users()

    def create_subscription(self, user_id: int, plan: str, **kwargs) -> Subscription:
        """Create a new subscription for a user."""
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise UserNotFoundException(f"User with ID {user_id} not found")

        if plan not in [SubscriptionPlan.FREE, SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE]:
            raise ValidationException(f"Invalid plan: {plan}")

        existing = self.repository.get_by_user_id(user_id)
        if existing:
            raise ValidationException("User already has a subscription")

        end_date = None
        if plan != SubscriptionPlan.FREE:
            duration_days = kwargs.get('duration_days', 30)
            end_date = timezone.now() + timedelta(days=duration_days)

        subscription = self.repository.create(
            user=user,
            plan=plan,
            status=SubscriptionStatus.ACTIVE,
            start_date=timezone.now(),
            end_date=end_date,
            auto_renew=kwargs.get('auto_renew', False),
            payment_method=kwargs.get('payment_method'),
            amount_paid=kwargs.get('amount_paid', 0.00)
        )
        return subscription

    def upgrade_subscription(self, user_id: int, new_plan: str, **kwargs) -> Subscription:
        """Upgrade a user's subscription."""
        subscription = self.get_user_subscription(user_id)

        if new_plan not in [SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE]:
            raise ValidationException(f"Invalid plan for upgrade: {new_plan}")

        duration_days = kwargs.get('duration_days', 30)
        end_date = timezone.now() + timedelta(days=duration_days)

        subscription.upgrade_plan(new_plan, end_date=end_date)
        if kwargs.get('payment_method'):
            subscription.payment_method = kwargs['payment_method']
        if kwargs.get('amount_paid'):
            subscription.amount_paid = kwargs['amount_paid']
        subscription.save()

        return subscription

    def cancel_subscription(self, user_id: int) -> Subscription:
        """Cancel a user's subscription."""
        subscription = self.get_user_subscription(user_id)
        subscription.cancel()
        return subscription

    def check_premium_access(self, user_id: int) -> bool:
        """Check if user has premium access."""
        subscription = self.repository.get_by_user_id(user_id)
        if not subscription:
            return False
        return subscription.can_access_premium_content()

    def get_subscription_stats(self) -> dict:
        """Get subscription statistics."""
        return self.repository.get_stats()
