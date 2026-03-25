"""
Subscription serializers.
N-layered architecture: Serializer layer.
"""

from rest_framework import serializers
from app.models.models import Subscription, SubscriptionPlan, SubscriptionStatus
from app.api.serializers.user_serializers import UserSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for subscription data."""
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    user = UserSerializer(read_only=True)
    is_premium = serializers.BooleanField(read_only=True)
    days_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'plan_display', 'status', 'status_display',
            'start_date', 'end_date', 'auto_renew', 'payment_method',
            'amount_paid', 'is_premium', 'days_remaining',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubscriptionUpgradeSerializer(serializers.Serializer):
    """Serializer for upgrading subscription."""
    plan = serializers.CharField()
    duration_days = serializers.IntegerField(required=False, default=30)
    payment_method = serializers.CharField(required=False)
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0.00)

    def validate_plan(self, value):
        valid_plans = [SubscriptionPlan.BASIC, SubscriptionPlan.PREMIUM, SubscriptionPlan.ENTERPRISE]
        if value not in valid_plans:
            raise serializers.ValidationError(f"Invalid plan for upgrade: {value}")
        return value


class SubscriptionStatsSerializer(serializers.Serializer):
    """Serializer for subscription statistics."""
    total_subscriptions = serializers.IntegerField()
    free_users = serializers.IntegerField()
    basic_users = serializers.IntegerField()
    premium_users = serializers.IntegerField()
    enterprise_users = serializers.IntegerField()
    active = serializers.IntegerField()
    expired = serializers.IntegerField()
    cancelled = serializers.IntegerField()


class PremiumUserSerializer(serializers.ModelSerializer):
    """Serializer for premium user list."""
    user = UserSerializer(read_only=True)
    plan_display = serializers.CharField(source='get_plan_display', read_only=True)

    class Meta:
        model = Subscription
        fields = ['id', 'user', 'plan', 'plan_display', 'status', 'start_date', 'end_date', 'days_remaining']
