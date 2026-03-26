"""
MCQ repositories - Data access layer for MCQs.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import MCQSet, MCQ
from app.core.logger import get_logger


logger = get_logger(__name__)


class MCQSetRepository:
    """Repository class for MCQSet data access operations."""

    @staticmethod
    def get_by_id(set_id: int) -> Optional[MCQSet]:
        logger.debug(f"get_by_id called with set_id={set_id}")
        try:
            mcq_set = MCQSet.objects.get(id=set_id, is_active=True)
            logger.debug(f"MCQSet {set_id} retrieved: {mcq_set.title}")
            return mcq_set
        except MCQSet.DoesNotExist:
            logger.debug(f"MCQSet {set_id} not found")
            return None

    @staticmethod
    def get_by_topic(topic_id: int) -> List[MCQSet]:
        logger.debug(f"get_by_topic called with topic_id={topic_id}")
        sets = list(MCQSet.objects.filter(topic_id=topic_id, is_active=True))
        logger.debug(f"Retrieved {len(sets)} MCQ sets for topic {topic_id}")
        return sets

    @staticmethod
    def get_all() -> List[MCQSet]:
        logger.debug("get_all called")
        sets = list(MCQSet.objects.filter(is_active=True))
        logger.debug(f"Retrieved {len(sets)} MCQ sets")
        return sets

    @staticmethod
    def create(**kwargs) -> MCQSet:
        logger.info(f"Creating MCQSet: {kwargs.get('title', 'unknown')}")
        mcq_set = MCQSet.objects.create(**kwargs)
        logger.info(f"MCQSet created: ID={mcq_set.id}, title={mcq_set.title}")
        return mcq_set

    @staticmethod
    def update(mcq_set: MCQSet, **kwargs) -> MCQSet:
        logger.debug(f"Updating MCQSet {mcq_set.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(mcq_set, key) and key not in ['id']:
                setattr(mcq_set, key, value)
        mcq_set.save()
        logger.debug(f"MCQSet {mcq_set.id} updated successfully")
        return mcq_set

    @staticmethod
    def delete(mcq_set: MCQSet) -> None:
        logger.info(f"Deleting MCQSet {mcq_set.id}")
        mcq_set.is_active = False
        mcq_set.save()
        logger.info(f"MCQSet {mcq_set.id} deleted")


class MCQRepository:
    """Repository class for MCQ data access operations."""

    @staticmethod
    def get_by_id(mcq_id: int) -> Optional[MCQ]:
        logger.debug(f"get_by_id called with mcq_id={mcq_id}")
        try:
            mcq = MCQ.objects.get(id=mcq_id, is_active=True)
            logger.debug(f"MCQ {mcq_id} retrieved")
            return mcq
        except MCQ.DoesNotExist:
            logger.debug(f"MCQ {mcq_id} not found")
            return None

    @staticmethod
    def get_by_set(set_id: int) -> List[MCQ]:
        logger.debug(f"get_by_set called with set_id={set_id}")
        mcqs = list(MCQ.objects.filter(mcq_set_id=set_id, is_active=True))
        logger.debug(f"Retrieved {len(mcqs)} MCQs for set {set_id}")
        return mcqs

    @staticmethod
    def get_all() -> List[MCQ]:
        logger.debug("get_all called")
        mcqs = list(MCQ.objects.filter(is_active=True))
        logger.debug(f"Retrieved {len(mcqs)} MCQs")
        return mcqs

    @staticmethod
    def create(**kwargs) -> MCQ:
        logger.info(f"Creating MCQ in set {kwargs.get('mcq_set_id', 'unknown')}")
        mcq = MCQ.objects.create(**kwargs)
        logger.info(f"MCQ created: ID={mcq.id}")
        return mcq

    @staticmethod
    def update(mcq: MCQ, **kwargs) -> MCQ:
        logger.debug(f"Updating MCQ {mcq.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(mcq, key) and key not in ['id']:
                setattr(mcq, key, value)
        mcq.save()
        logger.debug(f"MCQ {mcq.id} updated successfully")
        return mcq

    @staticmethod
    def delete(mcq: MCQ) -> None:
        logger.info(f"Deleting MCQ {mcq.id}")
        mcq.is_active = False
        mcq.save()
        logger.info(f"MCQ {mcq.id} deleted")

    @staticmethod
    def count_by_set(set_id: int) -> int:
        logger.debug(f"count_by_set called with set_id={set_id}")
        count = MCQ.objects.filter(mcq_set_id=set_id, is_active=True).count()
        logger.debug(f"MCQs in set {set_id}: {count}")
        return count
