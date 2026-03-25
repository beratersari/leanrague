"""
Flashcard repositories - Data access layer for flashcards.
N-layered architecture: Repository layer.
"""

from typing import Optional, List
from app.models.models import FlashcardSet, Flashcard


class FlashcardSetRepository:
    """Repository class for FlashcardSet data access operations."""

    @staticmethod
    def get_by_id(set_id: int) -> Optional[FlashcardSet]:
        try:
            return FlashcardSet.objects.get(id=set_id, is_active=True)
        except FlashcardSet.DoesNotExist:
            return None

    @staticmethod
    def get_by_topic(topic_id: int) -> List[FlashcardSet]:
        return list(FlashcardSet.objects.filter(topic_id=topic_id, is_active=True))

    @staticmethod
    def get_all() -> List[FlashcardSet]:
        return list(FlashcardSet.objects.filter(is_active=True))

    @staticmethod
    def create(**kwargs) -> FlashcardSet:
        return FlashcardSet.objects.create(**kwargs)

    @staticmethod
    def update(fc_set: FlashcardSet, **kwargs) -> FlashcardSet:
        for key, value in kwargs.items():
            if hasattr(fc_set, key) and key not in ['id']:
                setattr(fc_set, key, value)
        fc_set.save()
        return fc_set

    @staticmethod
    def delete(fc_set: FlashcardSet) -> None:
        fc_set.is_active = False
        fc_set.save()


class FlashcardRepository:
    """Repository class for Flashcard data access operations."""

    @staticmethod
    def get_by_id(card_id: int) -> Optional[Flashcard]:
        try:
            return Flashcard.objects.get(id=card_id, is_active=True)
        except Flashcard.DoesNotExist:
            return None

    @staticmethod
    def get_by_set(set_id: int) -> List[Flashcard]:
        return list(Flashcard.objects.filter(flashcard_set_id=set_id, is_active=True))

    @staticmethod
    def get_all() -> List[Flashcard]:
        return list(Flashcard.objects.filter(is_active=True))

    @staticmethod
    def create(**kwargs) -> Flashcard:
        return Flashcard.objects.create(**kwargs)

    @staticmethod
    def update(card: Flashcard, **kwargs) -> Flashcard:
        for key, value in kwargs.items():
            if hasattr(card, key) and key not in ['id']:
                setattr(card, key, value)
        card.save()
        return card

    @staticmethod
    def delete(card: Flashcard) -> None:
        card.is_active = False
        card.save()

    @staticmethod
    def count_by_set(set_id: int) -> int:
        return Flashcard.objects.filter(flashcard_set_id=set_id, is_active=True).count()
