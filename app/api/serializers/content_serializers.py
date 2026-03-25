"""
Content serializers - Topic, Flashcard, MCQ.
N-layered architecture: Serializer layer.
"""

from rest_framework import serializers
from app.models.models import Topic, FlashcardSet, Flashcard, MCQSet, MCQ


# =============================================================================
# TOPIC SERIALIZERS
# =============================================================================

class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic."""
    flashcard_count = serializers.ReadOnlyField()
    mcq_count = serializers.ReadOnlyField()
    flashcard_sets_count = serializers.SerializerMethodField()
    mcq_sets_count = serializers.SerializerMethodField()

    class Meta:
        model = Topic
        fields = [
            'id', 'name', 'description', 'icon', 'is_active', 'is_premium', 'order',
            'flashcard_count', 'mcq_count', 'flashcard_sets_count', 'mcq_sets_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_flashcard_sets_count(self, obj):
        return obj.flashcard_sets.filter(is_active=True).count()

    def get_mcq_sets_count(self, obj):
        return obj.mcq_sets.filter(is_active=True).count()


class TopicListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Topic listing."""
    flashcard_count = serializers.ReadOnlyField()
    mcq_count = serializers.ReadOnlyField()

    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'icon', 'is_premium', 'flashcard_count', 'mcq_count', 'order']


# =============================================================================
# FLASHCARD SERIALIZERS
# =============================================================================

class FlashcardSerializer(serializers.ModelSerializer):
    """Serializer for Flashcard."""
    flashcard_set_name = serializers.CharField(source='flashcard_set.name', read_only=True)
    topic_name = serializers.CharField(source='flashcard_set.topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='flashcard_set.topic.id', read_only=True)

    class Meta:
        model = Flashcard
        fields = [
            'id', 'flashcard_set', 'flashcard_set_name', 'topic_id', 'topic_name',
            'front', 'back', 'front_audio', 'back_audio', 'image_url',
            'example_sentence', 'hint', 'is_active', 'is_premium', 'order',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class FlashcardSetSerializer(serializers.ModelSerializer):
    """Serializer for FlashcardSet with flashcards count."""
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='topic.id', read_only=True)
    flashcards_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashcardSet
        fields = [
            'id', 'topic', 'topic_id', 'topic_name',
            'name', 'description', 'is_active', 'is_premium', 'order',
            'flashcards_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_flashcards_count(self, obj):
        return obj.flashcards.filter(is_active=True).count()


class FlashcardSetDetailSerializer(FlashcardSetSerializer):
    """Detailed serializer for FlashcardSet with flashcards."""
    flashcards = FlashcardSerializer(many=True, read_only=True)

    class Meta(FlashcardSetSerializer.Meta):
        fields = FlashcardSetSerializer.Meta.fields + ['flashcards']


class FlashcardListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Flashcard listing."""
    class Meta:
        model = Flashcard
        fields = ['id', 'front', 'back', 'image_url', 'is_premium', 'order']


# =============================================================================
# MCQ SERIALIZERS
# =============================================================================

class MCQSerializer(serializers.ModelSerializer):
    """Serializer for MCQ with answer checking."""
    mcq_set_name = serializers.CharField(source='mcq_set.name', read_only=True)
    topic_name = serializers.CharField(source='mcq_set.topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='mcq_set.topic.id', read_only=True)

    class Meta:
        model = MCQ
        fields = [
            'id', 'mcq_set', 'mcq_set_name', 'topic_id', 'topic_name',
            'question', 'option_a', 'option_b', 'option_c', 'option_d',
            'correct_option', 'explanation', 'audio_url', 'image_url',
            'hint', 'is_active', 'is_premium', 'order', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MCQPublicSerializer(serializers.ModelSerializer):
    """Serializer for MCQ without revealing correct answer (for quiz)."""
    mcq_set_name = serializers.CharField(source='mcq_set.name', read_only=True)
    topic_name = serializers.CharField(source='mcq_set.topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='mcq_set.topic.id', read_only=True)

    class Meta:
        model = MCQ
        fields = [
            'id', 'mcq_set', 'mcq_set_name', 'topic_id', 'topic_name',
            'question', 'option_a', 'option_b', 'option_c', 'option_d',
            'audio_url', 'image_url', 'hint', 'is_premium', 'order'
        ]


class MCQSetSerializer(serializers.ModelSerializer):
    """Serializer for MCQSet with MCQs count."""
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    topic_id = serializers.IntegerField(source='topic.id', read_only=True)
    mcqs_count = serializers.SerializerMethodField()

    class Meta:
        model = MCQSet
        fields = [
            'id', 'topic', 'topic_id', 'topic_name',
            'name', 'description', 'is_active', 'is_premium', 'order',
            'mcqs_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_mcqs_count(self, obj):
        return obj.mcqs.filter(is_active=True).count()


class MCQSetDetailSerializer(MCQSetSerializer):
    """Detailed serializer for MCQSet with MCQs."""
    mcqs = MCQSerializer(many=True, read_only=True)

    class Meta(MCQSetSerializer.Meta):
        fields = MCQSetSerializer.Meta.fields + ['mcqs']


class MCQListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for MCQ listing."""
    class Meta:
        model = MCQ
        fields = ['id', 'question', 'option_a', 'option_b', 'option_c', 'option_d', 'is_premium', 'order']


class MCQAnswerSerializer(serializers.Serializer):
    """Serializer for submitting MCQ answers."""
    mcq_id = serializers.IntegerField()
    user_answer = serializers.CharField(max_length=1)

    def validate_user_answer(self, value):
        if value.upper() not in ['A', 'B', 'C', 'D']:
            raise serializers.ValidationError("Answer must be A, B, C, or D")
        return value.upper()
