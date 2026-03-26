"""
MCQ services - Business logic for MCQs.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import MCQSet, MCQ
from app.repositories.mcq_repository import MCQSetRepository, MCQRepository
from app.core.logger import get_logger


class MCQSetService:
    """Service class for MCQSet business logic."""

    def __init__(self):
        self.repository = MCQSetRepository()
        self.logger = get_logger(__name__)

    def get_set(self, set_id: int) -> Optional[MCQSet]:
        self.logger.debug(f"get_set called with set_id={set_id}")
        mcq_set = self.repository.get_by_id(set_id)
        if mcq_set:
            self.logger.debug(f"MCQSet {set_id} found: {mcq_set.title}")
        else:
            self.logger.debug(f"MCQSet {set_id} not found")
        return mcq_set

    def list_sets(self, topic_id: Optional[int] = None) -> List[MCQSet]:
        self.logger.debug(f"list_sets called with topic_id={topic_id}")
        if topic_id:
            sets = self.repository.get_by_topic(topic_id)
            self.logger.info(f"Listed {len(sets)} MCQ sets for topic {topic_id}")
        else:
            sets = self.repository.get_all()
            self.logger.info(f"Listed all {len(sets)} MCQ sets")
        return sets

    def create_set(self, **kwargs) -> MCQSet:
        self.logger.info(f"Creating MCQ set: {kwargs.get('title', 'unknown')}")
        mcq_set = self.repository.create(**kwargs)
        self.logger.info(f"MCQSet created: ID={mcq_set.id}, title={mcq_set.title}")
        return mcq_set

    def update_set(self, set_id: int, **kwargs) -> Optional[MCQSet]:
        self.logger.info(f"Updating MCQSet {set_id} with {kwargs}")
        mcq_set = self.get_set(set_id)
        if mcq_set:
            updated = self.repository.update(mcq_set, **kwargs)
            self.logger.info(f"MCQSet {set_id} updated successfully")
            return updated
        self.logger.warning(f"MCQSet {set_id} not found for update")
        return None

    def delete_set(self, set_id: int) -> bool:
        self.logger.info(f"Deleting MCQSet {set_id}")
        mcq_set = self.get_set(set_id)
        if mcq_set:
            self.repository.delete(mcq_set)
            self.logger.info(f"MCQSet {set_id} deleted successfully")
            return True
        self.logger.warning(f"MCQSet {set_id} not found for deletion")
        return False


class MCQService:
    """Service class for MCQ business logic."""

    def __init__(self):
        self.repository = MCQRepository()
        self.logger = get_logger(__name__)

    def get_mcq(self, mcq_id: int) -> Optional[MCQ]:
        self.logger.debug(f"get_mcq called with mcq_id={mcq_id}")
        mcq = self.repository.get_by_id(mcq_id)
        if mcq:
            self.logger.debug(f"MCQ {mcq_id} found")
        else:
            self.logger.debug(f"MCQ {mcq_id} not found")
        return mcq

    def list_mcqs(self, set_id: Optional[int] = None) -> List[MCQ]:
        self.logger.debug(f"list_mcqs called with set_id={set_id}")
        if set_id:
            mcqs = self.repository.get_by_set(set_id)
            self.logger.info(f"Listed {len(mcqs)} MCQs for set {set_id}")
        else:
            mcqs = self.repository.get_all()
            self.logger.info(f"Listed all {len(mcqs)} MCQs")
        return mcqs

    def create_mcq(self, **kwargs) -> MCQ:
        self.logger.info(f"Creating MCQ in set {kwargs.get('mcq_set_id', 'unknown')}")
        mcq = self.repository.create(**kwargs)
        self.logger.info(f"MCQ created: ID={mcq.id}")
        return mcq

    def update_mcq(self, mcq_id: int, **kwargs) -> Optional[MCQ]:
        self.logger.info(f"Updating MCQ {mcq_id} with {kwargs}")
        mcq = self.get_mcq(mcq_id)
        if mcq:
            updated = self.repository.update(mcq, **kwargs)
            self.logger.info(f"MCQ {mcq_id} updated successfully")
            return updated
        self.logger.warning(f"MCQ {mcq_id} not found for update")
        return None

    def delete_mcq(self, mcq_id: int) -> bool:
        self.logger.info(f"Deleting MCQ {mcq_id}")
        mcq = self.get_mcq(mcq_id)
        if mcq:
            self.repository.delete(mcq)
            self.logger.info(f"MCQ {mcq_id} deleted successfully")
            return True
        self.logger.warning(f"MCQ {mcq_id} not found for deletion")
        return False

    def check_answer(self, mcq_id: int, user_answer: str) -> dict:
        self.logger.debug(f"check_answer called for MCQ {mcq_id} with answer {user_answer}")
        mcq = self.get_mcq(mcq_id)
        if not mcq:
            self.logger.warning(f"MCQ {mcq_id} not found for answer check")
            return {'correct': False, 'error': 'MCQ not found'}
        
        is_correct = mcq.check_answer(user_answer)
        self.logger.info(f"MCQ {mcq_id} answer check: user={user_answer}, correct={is_correct}")
        return {
            'correct': is_correct,
            'correct_option': mcq.correct_option,
            'correct_answer': mcq.correct_answer,
            'explanation': mcq.explanation,
        }

    def get_random_mcqs(self, set_id: int, count: int = 10) -> List[MCQ]:
        self.logger.debug(f"get_random_mcqs called with set_id={set_id}, count={count}")
        import random
        mcqs = self.list_mcqs(set_id)
        result = random.sample(mcqs, min(count, len(mcqs))) if mcqs else []
        self.logger.info(f"Retrieved {len(result)} random MCQs from set {set_id}")
        return result
