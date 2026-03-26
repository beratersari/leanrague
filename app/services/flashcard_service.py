"""
Flashcard services - Business logic for flashcards.
N-layered architecture: Service layer.
"""

from typing import Optional, List
from app.models.models import FlashcardSet, Flashcard
from app.repositories.flashcard_repository import FlashcardSetRepository, FlashcardRepository
from app.core.logger import get_logger


class FlashcardSetService:
    """Service class for FlashcardSet business logic."""

    def __init__(self):
        self.repository = FlashcardSetRepository()
        self.logger = get_logger(__name__)

    def get_set(self, set_id: int) -> Optional[FlashcardSet]:
        self.logger.debug(f"get_set called with set_id={set_id}")
        fc_set = self.repository.get_by_id(set_id)
        if fc_set:
            self.logger.debug(f"FlashcardSet {set_id} found: {fc_set.title}")
        else:
            self.logger.debug(f"FlashcardSet {set_id} not found")
        return fc_set

    def list_sets(self, topic_id: Optional[int] = None) -> List[FlashcardSet]:
        self.logger.debug(f"list_sets called with topic_id={topic_id}")
        if topic_id:
            sets = self.repository.get_by_topic(topic_id)
            self.logger.info(f"Listed {len(sets)} flashcard sets for topic {topic_id}")
        else:
            sets = self.repository.get_all()
            self.logger.info(f"Listed all {len(sets)} flashcard sets")
        return sets

    def create_set(self, **kwargs) -> FlashcardSet:
        self.logger.info(f"Creating flashcard set: {kwargs.get('title', 'unknown')}")
        fc_set = self.repository.create(**kwargs)
        self.logger.info(f"FlashcardSet created: ID={fc_set.id}, title={fc_set.title}")
        return fc_set

    def update_set(self, set_id: int, **kwargs) -> Optional[FlashcardSet]:
        self.logger.info(f"Updating FlashcardSet {set_id} with {kwargs}")
        fc_set = self.get_set(set_id)
        if fc_set:
            updated = self.repository.update(fc_set, **kwargs)
            self.logger.info(f"FlashcardSet {set_id} updated successfully")
            return updated
        self.logger.warning(f"FlashcardSet {set_id} not found for update")
        return None

    def delete_set(self, set_id: int) -> bool:
        self.logger.info(f"Deleting FlashcardSet {set_id}")
        fc_set = self.get_set(set_id)
        if fc_set:
            self.repository.delete(fc_set)
            self.logger.info(f"FlashcardSet {set_id} deleted successfully")
            return True
        self.logger.warning(f"FlashcardSet {set_id} not found for deletion")
        return False


class FlashcardService:
    """Service class for Flashcard business logic."""

    def __init__(self):
        self.repository = FlashcardRepository()
        self.logger = get_logger(__name__)

    def get_card(self, card_id: int) -> Optional[Flashcard]:
        self.logger.debug(f"get_card called with card_id={card_id}")
        card = self.repository.get_by_id(card_id)
        if card:
            self.logger.debug(f"Flashcard {card_id} found")
        else:
            self.logger.debug(f"Flashcard {card_id} not found")
        return card

    def list_cards(self, set_id: Optional[int] = None) -> List[Flashcard]:
        self.logger.debug(f"list_cards called with set_id={set_id}")
        if set_id:
            cards = self.repository.get_by_set(set_id)
            self.logger.info(f"Listed {len(cards)} flashcards for set {set_id}")
        else:
            cards = self.repository.get_all()
            self.logger.info(f"Listed all {len(cards)} flashcards")
        return cards

    def create_card(self, **kwargs) -> Flashcard:
        self.logger.info(f"Creating flashcard in set {kwargs.get('flashcard_set_id', 'unknown')}")
        card = self.repository.create(**kwargs)
        self.logger.info(f"Flashcard created: ID={card.id}")
        return card

    def update_card(self, card_id: int, **kwargs) -> Optional[Flashcard]:
        self.logger.info(f"Updating Flashcard {card_id} with {kwargs}")
        card = self.get_card(card_id)
        if card:
            updated = self.repository.update(card, **kwargs)
            self.logger.info(f"Flashcard {card_id} updated successfully")
            return updated
        self.logger.warning(f"Flashcard {card_id} not found for update")
        return None

    def delete_card(self, card_id: int) -> bool:
        self.logger.info(f"Deleting Flashcard {card_id}")
        card = self.get_card(card_id)
        if card:
            self.repository.delete(card)
            self.logger.info(f"Flashcard {card_id} deleted successfully")
            return True
        self.logger.warning(f"Flashcard {card_id} not found for deletion")
        return False

    def get_random_cards(self, set_id: int, count: int = 10) -> List[Flashcard]:
        self.logger.debug(f"get_random_cards called with set_id={set_id}, count={count}")
        import random
        cards = self.list_cards(set_id)
        result = random.sample(cards, min(count, len(cards))) if cards else []
        self.logger.info(f"Retrieved {len(result)} random flashcards from set {set_id}")
        return result
