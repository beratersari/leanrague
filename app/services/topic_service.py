"""
Topic service - Business logic for topics.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import Topic
from app.repositories.topic_repository import TopicRepository


class TopicService:
    """Service class for Topic business logic."""

    def __init__(self):
        self.repository = TopicRepository()

    def get_topic(self, topic_id: int) -> Optional[Topic]:
        return self.repository.get_by_id(topic_id)

    def list_topics(self) -> List[Topic]:
        return self.repository.get_all()

    def create_topic(self, **kwargs) -> Topic:
        return self.repository.create(**kwargs)

    def update_topic(self, topic_id: int, **kwargs) -> Optional[Topic]:
        topic = self.get_topic(topic_id)
        if topic:
            return self.repository.update(topic, **kwargs)
        return None

    def delete_topic(self, topic_id: int) -> bool:
        topic = self.get_topic(topic_id)
        if topic:
            self.repository.delete(topic)
            return True
        return False
