"""
Topic service - Business logic for topics.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import Topic
from app.repositories.topic_repository import TopicRepository
from app.core.logger import get_logger


class TopicService:
    """Service class for Topic business logic."""

    def __init__(self):
        self.repository = TopicRepository()
        self.logger = get_logger(__name__)

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        self.logger.debug(f"get_topic called with topic_id={topic_id}")
        topic = self.repository.get_by_id(topic_id)
        if topic:
            self.logger.debug(f"Topic {topic_id} found: {topic.title}")
        else:
            self.logger.debug(f"Topic {topic_id} not found")
        return topic

    def list_topics(self) -> List[Topic]:
        self.logger.debug("list_topics called")
        topics = self.repository.get_all()
        self.logger.info(f"Listed {len(topics)} topics")
        return topics

    def create_topic(self, **kwargs) -> Topic:
        self.logger.info(f"Creating topic: {kwargs.get('title', 'unknown')}")
        topic = self.repository.create(**kwargs)
        self.logger.info(f"Topic created: ID={topic.id}, title={topic.title}")
        return topic

    def update_topic(self, topic_id: int, **kwargs) -> Optional[Topic]:
        self.logger.info(f"Updating topic {topic_id} with {kwargs}")
        topic = self.get_topic(topic_id)
        if topic:
            updated = self.repository.update(topic, **kwargs)
            self.logger.info(f"Topic {topic_id} updated successfully")
            return updated
        self.logger.warning(f"Topic {topic_id} not found for update")
        return None

    def delete_topic(self, topic_id: int) -> bool:
        self.logger.info(f"Deleting topic {topic_id}")
        topic = self.get_topic(topic_id)
        if topic:
            self.repository.delete(topic)
            self.logger.info(f"Topic {topic_id} deleted successfully")
            return True
        self.logger.warning(f"Topic {topic_id} not found for deletion")
        return False
