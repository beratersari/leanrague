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
from app.core.logger import get_logger


class SubscriptionService:
    """
    Service class for Subscription business logic operations.
    Contains all business rules and logic for subscription management.
    """

    def __init__(self):
        self.repository = SubscriptionRepository()
        self.user_repository = UserRepository()
        self.logger = get_logger(__name__)

    def get_subscription(self, subscription_id: int) -> Subscription:
        """Get a subscription by ID."""
        self.logger.debug(f"get_subscription called with subscription_id={subscription_id}")
        subscription = self.repository.get_by_id(subscription_id)
        if not subscription:
            self.logger.warning(f"Subscription {subscription_id} not found")
            raise SubscriptionNotFoundException(f"Subscription with ID {subscription_id} not found")
        self.logger.debug(f"Subscription {subscription_id} found: plan={subscription.plan}")
        return subscription

    def get_user_subscription(self, user_id: int) -> Optional[Subscription]:
        """Get subscription for a user, create if not exists."""
        self.logger.debug(f"get_user_subscription called for user_id={user_id}")
        subscription = self.repository.get_by_user_id(user_id)
        if not subscription:
            user = self.user_repository.get_by_id(user_id)
            if not user:
                self.logger.warning(f"User {user_id} not found for subscription")
                raise UserNotFoundException(f"User with ID {user_id} not found")
            subscription = self.repository.create(
                user=user,
                plan=SubscriptionPlan.FREE,
                status=SubscriptionStatus.ACTIVE
            )
            self.logger.info(f"Created default FREE subscription for user {user_id}")
        self.logger.debug(f"User {user_id} subscription: plan={subscription.plan}")
        return subscription

    def list_subscriptions(self, plan: Optional[str] = None, status: Optional[str] = None) -> List[Subscription]:
        """List subscriptions with optional filters."""
        self.logger.debug(f"list_subscriptions called: plan={plan}, status={status}")
        if plan:
            subscriptions = self.repository.get_by_plan(plan)
            self.logger.info(f"Listed {len(subscriptions)} subscriptions with plan {plan}")
        elif status:
            subscriptions = self.repository.get_by_status(status)
            self.logger.info(f"Listed {len(subscriptions)} subscriptions with status {status}")
        else:
            subscriptions = self.repository.get_all()
            self.logger.info(f"Listed all {len(subscriptions)} subscriptions")
        return subscriptions

    def get_premium_users(self) -> List[Subscription]:
        """Get all premium users."""
        self.logger.debug("get_premium_users called")
        premium = self.repository.get_premium_users()
        self.logger.info(f"Found {len(premium)} premium users")
        return premium

    def create_subscription(self, user_id: int, plan: str, **kwargs) -> Subscription:
        """Create a new subscription for a user."""
        self.logger.info(f"Creating {plan} subscription for user {user_id}")
        user = self.user_repository.get_by_id(user_id)
        if not user:
            self.logger.error(f"User {user_id} not found for subscription creation")
            raise UserNotFoundException(f"User with ID {user_id} not found")

        if plan not in [SubscriptionPlan.FREE, SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE]:
            self.logger.error(f"Invalid plan for subscription: {plan}")
            raise ValidationException(f"Invalid plan: {plan}")

        existing = self.repository.get_by_user_id(user_id)
        if existing:
            self.logger.warning(f"User {user_id} already has a subscription")
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
        self.logger.info(f"Subscription created: ID={subscription.id}, plan={plan}, user={user_id}")
        return subscription

    def upgrade_subscription(self, user_id: int, new_plan: str, **kwargs) -> Subscription:
        """Upgrade a user's subscription."""
        self.logger.info(f"Upgrading user {user_id} subscription to {new_plan}")
        subscription = self.get_user_subscription(user_id)

        if new_plan not in [SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE]:
            self.logger.error(f"Invalid plan for upgrade: {new_plan}")
            raise ValidationException(f"Invalid plan for upgrade: {new_plan}")

        duration_days = kwargs.get('duration_days', 30)
        end_date = timezone.now() + timedelta(days=duration_days)

        subscription.upgrade_plan(new_plan, end_date=end_date)
        if kwargs.get('payment_method'):
            subscription.payment_method = kwargs['payment_method']
        if kwargs.get('amount_paid'):
            subscription.amount_paid = kwargs['amount_paid']
        subscription.save()

        self.logger.info(f"Subscription upgraded: user={user_id}, new_plan={new_plan}")
        return subscription

    def cancel_subscription(self, user_id: int) -> Subscription:
        """Cancel a user's subscription."""
        self.logger.info(f"Cancelling subscription for user {user_id}")
        subscription = self.get_user_subscription(user_id)
        subscription.cancel()
        self.logger.info(f"Subscription cancelled for user {user_id}")
        return subscription

    def check_premium_access(self, user_id: int) -> bool:
        """Check if user has premium access."""
        self.logger.debug(f"check_premium_access called for user {user_id}")
        subscription = self.repository.get_by_user_id(user_id)
        if not subscription:
            self.logger.debug(f"User {user_id} has no subscription")
            return False
        has_access = subscription.can_access_premium_content()
        self.logger.debug(f"User {user_id} premium access: {has_access}")
        return has_access

    def get_subscription_stats(self) -> dict:
        """Get subscription statistics."""
        self.logger.debug("get_subscription_stats called")
        stats = self.repository.get_stats()
        self.logger.info(f"Subscription stats: {stats}")
        return stats
