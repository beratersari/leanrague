"""
Creator Field service - Business logic for creator fields (paid content packages).
N-layered architecture: Service layer.

Features:
- Creators can create fields with flashcard sets and MCQ sets
- Users must purchase each field separately (even if premium)
- Access control: only creator or purchasers can see content
"""

from typing import Optional, List
from decimal import Decimal
from django.utils import timezone

from app.models.models import (
    CustomUser,
    CreatorField,
    CreatorFieldPurchase,
    FlashcardSet,
    MCQSet,
)
from app.core.logger import get_logger


logger = get_logger(__name__)


class CreatorFieldService:
    """Service for CreatorField business logic."""

    def get_field(self, field_id: int) -> Optional[CreatorField]:
        logger.debug(f"get_field called with field_id={field_id}")
        try:
            return CreatorField.objects.get(id=field_id)
        except CreatorField.DoesNotExist:
            logger.debug(f"CreatorField {field_id} not found")
            return None

    def list_fields(self, creator_id: Optional[int] = None, public_only: bool = True) -> List[CreatorField]:
        """
        List creator fields.
        If public_only=True, only active fields are returned.
        """
        qs = CreatorField.objects.all()
        if public_only:
            qs = qs.filter(is_active=True)
        if creator_id:
            qs = qs.filter(creator_id=creator_id)
        return list(qs)

    def create_field(self, creator: CustomUser, **kwargs) -> CreatorField:
        """Create a new creator field."""
        logger.info(f"Creating CreatorField for creator {creator.email}")
        field = CreatorField.objects.create(creator=creator, **kwargs)
        logger.info(f"CreatorField created: ID={field.id}, name={field.name}")
        return field

    def update_field(self, field: CreatorField, **kwargs) -> CreatorField:
        """Update a creator field."""
        logger.info(f"Updating CreatorField {field.id}")
        for key, value in kwargs.items():
            if hasattr(field, key):
                setattr(field, key, value)
        field.save()
        logger.info(f"CreatorField {field.id} updated")
        return field

    def delete_field(self, field: CreatorField) -> bool:
        """Delete a creator field."""
        logger.info(f"Deleting CreatorField {field.id}")
        field.delete()
        return True

    def purchase_field(self, user: CustomUser, field: CreatorField) -> CreatorFieldPurchase:
        """Purchase a creator field for a user."""
        logger.info(f"User {user.email} purchasing field {field.id} ({field.name})")
        
        purchase, created = CreatorFieldPurchase.objects.get_or_create(
            user=user,
            creator_field=field,
            defaults={
                'amount_paid': field.price,
                'purchased_at': timezone.now(),
            }
        )
        if created:
            logger.info(f"Purchase created: user={user.id}, field={field.id}")
        else:
            logger.debug(f"User {user.email} already owns field {field.id}")
        return purchase

    def has_access(self, user: CustomUser, field: CreatorField) -> bool:
        """
        Check if user has access to a field.
        Access if: user is the creator OR user has purchased the field.
        """
        if field.creator_id == user.id:
            return True
        return field.is_purchased_by(user)

    def get_user_purchases(self, user: CustomUser) -> List[CreatorFieldPurchase]:
        """Get all field purchases for a user."""
        return list(CreatorFieldPurchase.objects.filter(user=user))

    def get_creator_fields(self, creator: CustomUser) -> List[CreatorField]:
        """Get all fields owned by a creator."""
        return list(CreatorField.objects.filter(creator=creator))
