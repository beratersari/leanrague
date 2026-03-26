"""
Topic repository - Data access layer for topics.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import Topic
from app.core.logger import get_logger


logger = get_logger(__name__)


class TopicRepository:
    """Repository class for Topic data access operations."""

    @staticmethod
    def get_by_id(topic_id: int) -> Optional[Topic]:
        logger.debug(f"get_by_id called with topic_id={topic_id}")
        try:
            topic = Topic.objects.get(id=topic_id, is_active=True)
            logger.debug(f"Topic {topic_id} retrieved: {topic.title}")
            return topic
        except Topic.DoesNotExist:
            logger.debug(f"Topic {topic_id} not found")
            return None

    @staticmethod
    def get_all() -> List[Topic]:
        logger.debug("get_all called")
        topics = list(Topic.objects.filter(is_active=True))
        logger.debug(f"Retrieved {len(topics)} topics")
        return topics

    @staticmethod
    def create(**kwargs) -> Topic:
        logger.info(f"Creating topic: {kwargs.get('title', 'unknown')}")
        topic = Topic.objects.create(**kwargs)
        logger.info(f"Topic created: ID={topic.id}, title={topic.title}")
        return topic

    @staticmethod
    def update(topic: Topic, **kwargs) -> Topic:
        logger.debug(f"Updating topic {topic.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(topic, key) and key not in ['id']:
                setattr(topic, key, value)
        topic.save()
        logger.debug(f"Topic {topic.id} updated successfully")
        return topic

    @staticmethod
    def delete(topic: Topic) -> None:
        logger.info(f"Deleting topic {topic.id}")
        topic.is_active = False
        topic.save()
        logger.info(f"Topic {topic.id} deleted")
