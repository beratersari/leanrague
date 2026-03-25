"""
Flashcard services - Business logic for flashcards.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import FlashcardSet, Flashcard
from app.repositories.flashcard_repository import FlashcardSetRepository, FlashcardRepository


class FlashcardSetService:
    """Service class for FlashcardSet business logic."""

    def __init__(self):
        self.repository = FlashcardSetRepository()

    def get_set(self, set_id: int) -> Optional[FlashcardSet]:
        return self.repository.get_by_id(set_id)

    def list_sets(self, topic_id: Optional[int] = None) -> List[FlashcardSet]:
        if topic_id:
            return self.repository.get_by_topic(topic_id)
        return self.repository.get_all()

    def create_set(self, **kwargs) -> FlashcardSet:
        return self.repository.create(**kwargs)

    def update_set(self, set_id: int, **kwargs) -> Optional[FlashcardSet]:
        fc_set = self.get_set(set_id)
        if fc_set:
            return self.repository.update(fc_set, **kwargs)
        return None

    def delete_set(self, set_id: int) -> bool:
        fc_set = self.get_set(set_id)
        if fc_set:
            self.repository.delete(fc_set)
            return True
        return False


class FlashcardService:
    """Service class for Flashcard business logic."""

    def __init__(self):
        self.repository = FlashcardRepository()

    def get_card(self, card_id: int) -> Optional[Flashcard]:
        return self.repository.get_by_id(card_id)

    def list_cards(self, set_id: Optional[int] = None) -> List[Flashcard]:
        if set_id:
            return self.repository.get_by_set(set_id)
        return self.repository.get_all()

    def create_card(self, **kwargs) -> Flashcard:
        return self.repository.create(**kwargs)

    def update_card(self, card_id: int, **kwargs) -> Optional[Flashcard]:
        card = self.get_card(card_id)
        if card:
            return self.repository.update(card, **kwargs)
        return None

    def delete_card(self, card_id: int) -> bool:
        card = self.get_card(card_id)
        if card:
            self.repository.delete(card)
            return True
        return False

    def get_random_cards(self, set_id: int, count: int = 10) -> List[Flashcard]:
        import random
        cards = self.list_cards(set_id)
        return random.sample(cards, min(count, len(cards))) if cards else []
