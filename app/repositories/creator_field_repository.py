"""
Creator Field repository - Data access for creator fields.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import CreatorField, CreatorFieldPurchase
from app.core.logger import get_logger


logger = get_logger(__name__)


class CreatorFieldRepository:
    """Repository for CreatorField data access."""

    @staticmethod
    def get_by_id(field_id: int) -> Optional[CreatorField]:
        logger.debug(f"get_by_id called with field_id={field_id}")
        try:
            return CreatorField.objects.get(id=field_id)
        except CreatorField.DoesNotExist:
            return None

    @staticmethod
    def get_all(active_only: bool = True) -> List[CreatorField]:
        qs = CreatorField.objects.all()
        if active_only:
            qs = qs.filter(is_active=True)
        return list(qs)

    @staticmethod
    def get_by_creator(creator_id: int) -> List[CreatorField]:
        return list(CreatorField.objects.filter(creator_id=creator_id))

    @staticmethod
    def create(**kwargs) -> CreatorField:
        return CreatorField.objects.create(**kwargs)

    @staticmethod
    def update(field: CreatorField, **kwargs) -> CreatorField:
        for key, value in kwargs.items():
            if hasattr(field, key) and key not in ['id', 'creator']:
                setattr(field, key, value)
        field.save()
        return field

    @staticmethod
    def delete(field: CreatorField) -> None:
        field.delete()


class CreatorFieldPurchaseRepository:
    """Repository for CreatorFieldPurchase data access."""

    @staticmethod
    def get_by_id(purchase_id: int) -> Optional[CreatorFieldPurchase]:
        try:
            return CreatorFieldPurchase.objects.get(id=purchase_id)
        except CreatorFieldPurchase.DoesNotExist:
            return None

    @staticmethod
    def get_by_user(user_id: int) -> List[CreatorFieldPurchase]:
        return list(CreatorFieldPurchase.objects.filter(user_id=user_id))

    @staticmethod
    def get_by_user_and_field(user_id: int, field_id: int) -> Optional[CreatorFieldPurchase]:
        try:
            return CreatorFieldPurchase.objects.get(user_id=user_id, creator_field_id=field_id)
        except CreatorFieldPurchase.DoesNotExist:
            return None

    @staticmethod
    def create(**kwargs) -> CreatorFieldPurchase:
        return CreatorFieldPurchase.objects.create(**kwargs)

    @staticmethod
    def exists(user_id: int, field_id: int) -> bool:
        return CreatorFieldPurchase.objects.filter(user_id=user_id, creator_field_id=field_id).exists()
