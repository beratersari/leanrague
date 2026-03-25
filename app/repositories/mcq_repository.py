"""
MCQ repositories - Data access layer for MCQs.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import MCQSet, MCQ


class MCQSetRepository:
    """Repository class for MCQSet data access operations."""

    @staticmethod
    def get_by_id(set_id: int) -> Optional[MCQSet]:
        try:
            return MCQSet.objects.get(id=set_id, is_active=True)
        except MCQSet.DoesNotExist:
            return None

    @staticmethod
    def get_by_topic(topic_id: int) -> List[MCQSet]:
        return list(MCQSet.objects.filter(topic_id=topic_id, is_active=True))

    @staticmethod
    def get_all() -> List[MCQSet]:
        return list(MCQSet.objects.filter(is_active=True))

    @staticmethod
    def create(**kwargs) -> MCQSet:
        return MCQSet.objects.create(**kwargs)

    @staticmethod
    def update(mcq_set: MCQSet, **kwargs) -> MCQSet:
        for key, value in kwargs.items():
            if hasattr(mcq_set, key) and key not in ['id']:
                setattr(mcq_set, key, value)
        mcq_set.save()
        return mcq_set

    @staticmethod
    def delete(mcq_set: MCQSet) -> None:
        mcq_set.is_active = False
        mcq_set.save()


class MCQRepository:
    """Repository class for MCQ data access operations."""

    @staticmethod
    def get_by_id(mcq_id: int) -> Optional[MCQ]:
        try:
            return MCQ.objects.get(id=mcq_id, is_active=True)
        except MCQ.DoesNotExist:
            return None

    @staticmethod
    def get_by_set(set_id: int) -> List[MCQ]:
        return list(MCQ.objects.filter(mcq_set_id=set_id, is_active=True))

    @staticmethod
    def get_all() -> List[MCQ]:
        return list(MCQ.objects.filter(is_active=True))

    @staticmethod
    def create(**kwargs) -> MCQ:
        return MCQ.objects.create(**kwargs)

    @staticmethod
    def update(mcq: MCQ, **kwargs) -> MCQ:
        for key, value in kwargs.items():
            if hasattr(mcq, key) and key not in ['id']:
                setattr(mcq, key, value)
        mcq.save()
        return mcq

    @staticmethod
    def delete(mcq: MCQ) -> None:
        mcq.is_active = False
        mcq.save()

    @staticmethod
    def count_by_set(set_id: int) -> int:
        return MCQ.objects.filter(mcq_set_id=set_id, is_active=True).count()
