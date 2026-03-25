"""
Topic repository - Data access layer for topics.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import Topic


class TopicRepository:
    """Repository class for Topic data access operations."""

    @staticmethod
    def get_by_id(topic_id: int) -> Optional[Topic]:
        try:
            return Topic.objects.get(id=topic_id, is_active=True)
        except Topic.DoesNotExist:
            return None

    @staticmethod
    def get_all() -> List[Topic]:
        return list(Topic.objects.filter(is_active=True))

    @staticmethod
    def create(**kwargs) -> Topic:
        return Topic.objects.create(**kwargs)

    @staticmethod
    def update(topic: Topic, **kwargs) -> Topic:
        for key, value in kwargs.items():
            if hasattr(topic, key) and key not in ['id']:
                setattr(topic, key, value)
        topic.save()
        return topic

    @staticmethod
    def delete(topic: Topic) -> None:
        topic.is_active = False
        topic.save()
