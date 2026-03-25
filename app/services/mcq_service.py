"""
MCQ services - Business logic for MCQs.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import MCQSet, MCQ
from app.repositories.mcq_repository import MCQSetRepository, MCQRepository


class MCQSetService:
    """Service class for MCQSet business logic."""

    def __init__(self):
        self.repository = MCQSetRepository()

    def get_set(self, set_id: int) -> Optional[MCQSet]:
        return self.repository.get_by_id(set_id)

    def list_sets(self, topic_id: Optional[int] = None) -> List[MCQSet]:
        if topic_id:
            return self.repository.get_by_topic(topic_id)
        return self.repository.get_all()

    def create_set(self, **kwargs) -> MCQSet:
        return self.repository.create(**kwargs)

    def update_set(self, set_id: int, **kwargs) -> Optional[MCQSet]:
        mcq_set = self.get_set(set_id)
        if mcq_set:
            return self.repository.update(mcq_set, **kwargs)
        return None

    def delete_set(self, set_id: int) -> bool:
        mcq_set = self.get_set(set_id)
        if mcq_set:
            self.repository.delete(mcq_set)
            return True
        return False


class MCQService:
    """Service class for MCQ business logic."""

    def __init__(self):
        self.repository = MCQRepository()

    def get_mcq(self, mcq_id: int) -> Optional[MCQ]:
        return self.repository.get_by_id(mcq_id)

    def list_mcqs(self, set_id: Optional[int] = None) -> List[MCQ]:
        if set_id:
            return self.repository.get_by_set(set_id)
        return self.repository.get_all()

    def create_mcq(self, **kwargs) -> MCQ:
        return self.repository.create(**kwargs)

    def update_mcq(self, mcq_id: int, **kwargs) -> Optional[MCQ]:
        mcq = self.get_mcq(mcq_id)
        if mcq:
            return self.repository.update(mcq, **kwargs)
        return None

    def delete_mcq(self, mcq_id: int) -> bool:
        mcq = self.get_mcq(mcq_id)
        if mcq:
            self.repository.delete(mcq)
            return True
        return False

    def check_answer(self, mcq_id: int, user_answer: str) -> dict:
        mcq = self.get_mcq(mcq_id)
        if not mcq:
            return {'correct': False, 'error': 'MCQ not found'}
        
        is_correct = mcq.check_answer(user_answer)
        return {
            'correct': is_correct,
            'correct_option': mcq.correct_option,
            'correct_answer': mcq.correct_answer,
            'explanation': mcq.explanation,
        }

    def get_random_mcqs(self, set_id: int, count: int = 10) -> List[MCQ]:
        import random
        mcqs = self.list_mcqs(set_id)
        return random.sample(mcqs, min(count, len(mcqs))) if mcqs else []
