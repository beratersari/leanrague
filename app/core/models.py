"""
Core models - Base model classes for n-layered architecture.
"""

from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    An abstract base model that provides self-updating
    'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    An abstract base model that provides soft delete functionality.
    """
    is_active = models.BooleanField(default=True, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        """Soft delete the instance."""
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restore a soft-deleted instance."""
        self.is_active = True
        self.deleted_at = None
        self.save()
