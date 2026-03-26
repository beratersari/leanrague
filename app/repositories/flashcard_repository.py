"""
Flashcard repositories - Data access layer for flashcards.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import FlashcardSet, Flashcard
from app.core.logger import get_logger


logger = get_logger(__name__)


class FlashcardSetRepository:
    """Repository class for FlashcardSet data access operations."""

    @staticmethod
    def get_by_id(set_id: int) -> Optional[FlashcardSet]:
        logger.debug(f"get_by_id called with set_id={set_id}")
        try:
            fc_set = FlashcardSet.objects.get(id=set_id, is_active=True)
            logger.debug(f"FlashcardSet {set_id} retrieved: {fc_set.title}")
            return fc_set
        except FlashcardSet.DoesNotExist:
            logger.debug(f"FlashcardSet {set_id} not found")
            return None

    @staticmethod
    def get_by_topic(topic_id: int) -> List[FlashcardSet]:
        logger.debug(f"get_by_topic called with topic_id={topic_id}")
        sets = list(FlashcardSet.objects.filter(topic_id=topic_id, is_active=True))
        logger.debug(f"Retrieved {len(sets)} flashcard sets for topic {topic_id}")
        return sets

    @staticmethod
    def get_all() -> List[FlashcardSet]:
        logger.debug("get_all called")
        sets = list(FlashcardSet.objects.filter(is_active=True))
        logger.debug(f"Retrieved {len(sets)} flashcard sets")
        return sets

    @staticmethod
    def create(**kwargs) -> FlashcardSet:
        logger.info(f"Creating FlashcardSet: {kwargs.get('title', 'unknown')}")
        fc_set = FlashcardSet.objects.create(**kwargs)
        logger.info(f"FlashcardSet created: ID={fc_set.id}, title={fc_set.title}")
        return fc_set

    @staticmethod
    def update(fc_set: FlashcardSet, **kwargs) -> FlashcardSet:
        logger.debug(f"Updating FlashcardSet {fc_set.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(fc_set, key) and key not in ['id']:
                setattr(fc_set, key, value)
        fc_set.save()
        logger.debug(f"FlashcardSet {fc_set.id} updated successfully")
        return fc_set

    @staticmethod
    def delete(fc_set: FlashcardSet) -> None:
        logger.info(f"Deleting FlashcardSet {fc_set.id}")
        fc_set.is_active = False
        fc_set.save()
        logger.info(f"FlashcardSet {fc_set.id} deleted")


class FlashcardRepository:
    """Repository class for Flashcard data access operations."""

    @staticmethod
    def get_by_id(card_id: int) -> Optional[Flashcard]:
        logger.debug(f"get_by_id called with card_id={card_id}")
        try:
            card = Flashcard.objects.get(id=card_id, is_active=True)
            logger.debug(f"Flashcard {card_id} retrieved")
            return card
        except Flashcard.DoesNotExist:
            logger.debug(f"Flashcard {card_id} not found")
            return None

    @staticmethod
    def get_by_set(set_id: int) -> List[Flashcard]:
        logger.debug(f"get_by_set called with set_id={set_id}")
        cards = list(Flashcard.objects.filter(flashcard_set_id=set_id, is_active=True))
        logger.debug(f"Retrieved {len(cards)} flashcards for set {set_id}")
        return cards

    @staticmethod
    def get_all() -> List[Flashcard]:
        logger.debug("get_all called")
        cards = list(Flashcard.objects.filter(is_active=True))
        logger.debug(f"Retrieved {len(cards)} flashcards")
        return cards

    @staticmethod
    def create(**kwargs) -> Flashcard:
        logger.info(f"Creating Flashcard in set {kwargs.get('flashcard_set_id', 'unknown')}")
        card = Flashcard.objects.create(**kwargs)
        logger.info(f"Flashcard created: ID={card.id}")
        return card

    @staticmethod
    def update(card: Flashcard, **kwargs) -> Flashcard:
        logger.debug(f"Updating Flashcard {card.id} with {kwargs}")
        for key, value in kwargs.items():
            if hasattr(card, key) and key not in ['id']:
                setattr(card, key, value)
        card.save()
        logger.debug(f"Flashcard {card.id} updated successfully")
        return card

    @staticmethod
    def delete(card: Flashcard) -> None:
        logger.info(f"Deleting Flashcard {card.id}")
        card.is_active = False
        card.save()
        logger.info(f"Flashcard {card.id} deleted")

    @staticmethod
    def count_by_set(set_id: int) -> int:
        logger.debug(f"count_by_set called with set_id={set_id}")
        count = Flashcard.objects.filter(flashcard_set_id=set_id, is_active=True).count()
        logger.debug(f"Flashcards in set {set_id}: {count}")
        return count
