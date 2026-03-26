"""
Content views - Topic, Flashcard, MCQ endpoints.
N-layered architecture: API layer.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import Http404

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from app.permissions.role_permissions import IsAdmin, IsContentCreator
from app.services.topic_service import TopicService
from app.services.flashcard_service import FlashcardSetService, FlashcardService
from app.services.mcq_service import MCQSetService, MCQService
from app.api.serializers.content_serializers import (
    TopicSerializer, TopicListSerializer,
    FlashcardSerializer, FlashcardSetSerializer, FlashcardSetDetailSerializer, FlashcardListSerializer,
    MCQSerializer, MCQPublicSerializer, MCQSetSerializer, MCQSetDetailSerializer, MCQListSerializer, MCQAnswerSerializer
)
from app.core.logger import get_logger


logger = get_logger(__name__)


# =============================================================================
# HELPER MIXIN
# =============================================================================

class ServiceMixin:
    """Mixin to provide service instances."""
    @property
    def topic_service(self):
        if not hasattr(self, '_topic_service'):
            self._topic_service = TopicService()
        return self._topic_service

    @property
    def flashcard_set_service(self):
        if not hasattr(self, '_flashcard_set_service'):
            self._flashcard_set_service = FlashcardSetService()
        return self._flashcard_set_service

    @property
    def flashcard_service(self):
        if not hasattr(self, '_flashcard_service'):
            self._flashcard_service = FlashcardService()
        return self._flashcard_service

    @property
    def mcq_set_service(self):
        if not hasattr(self, '_mcq_set_service'):
            self._mcq_set_service = MCQSetService()
        return self._mcq_set_service

    @property
    def mcq_service(self):
        if not hasattr(self, '_mcq_service'):
            self._mcq_service = MCQService()
        return self._mcq_service

    def can_access_premium(self, request):
        """Check if user can access premium content."""
        return request.user.can_access_premium_content()


# =============================================================================
# TOPIC VIEWS
# =============================================================================

class TopicListView(ServiceMixin, APIView):
    """List all topics or create a new topic."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"TopicListView.get: user_id={request.user.id}, email={request.user.email}")
        topics = self.topic_service.list_topics()
        logger.debug(f"TopicListView.get: returning {len(topics)} topics")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = TopicListSerializer(topics, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"TopicListView.post: user_id={request.user.id}, email={request.user.email}")
        if not request.user.can_manage_content():
            logger.warning(f"TopicListView.post: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            topic = self.topic_service.create_topic(**serializer.validated_data)
            logger.info(f"TopicListView.post: topic created id={topic.id}")
            return Response(TopicSerializer(topic).data, status=status.HTTP_201_CREATED)
        logger.warning(f"TopicListView.post: validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicDetailView(ServiceMixin, APIView):
    """Retrieve, update, or delete a topic."""
    permission_classes = [IsAuthenticated]

    def get(self, request, topic_id):
        logger.debug(f"TopicDetailView.get: user_id={request.user.id}, topic_id={topic_id}")
        topic = self.topic_service.get_topic(topic_id)
        if not topic:
            logger.warning(f"TopicDetailView.get: topic {topic_id} not found")
            raise Http404("Topic not found")
        # Check premium access
        if topic.is_premium and not self.can_access_premium(request):
            logger.warning(f"TopicDetailView.get: premium denied for user_id={request.user.id}, topic_id={topic_id}")
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = TopicSerializer(topic)
        return Response(serializer.data)

    def put(self, request, topic_id):
        logger.info(f"TopicDetailView.put: user_id={request.user.id}, topic_id={topic_id}")
        if not request.user.can_manage_content():
            logger.warning(f"TopicDetailView.put: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        topic = self.topic_service.get_topic(topic_id)
        if not topic:
            logger.warning(f"TopicDetailView.put: topic {topic_id} not found")
            raise Http404("Topic not found")
        
        serializer = TopicSerializer(topic, data=request.data, partial=True)
        if serializer.is_valid():
            updated_topic = self.topic_service.update_topic(topic_id, **serializer.validated_data)
            logger.info(f"TopicDetailView.put: topic {topic_id} updated")
            return Response(TopicSerializer(updated_topic).data)
        logger.warning(f"TopicDetailView.put: validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, topic_id):
        logger.info(f"TopicDetailView.delete: user_id={request.user.id}, topic_id={topic_id}")
        if not request.user.can_manage_content():
            logger.warning(f"TopicDetailView.delete: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.topic_service.delete_topic(topic_id):
            logger.info(f"TopicDetailView.delete: topic {topic_id} deleted")
            return Response({'message': 'Topic deleted'}, status=status.HTTP_204_NO_CONTENT)
        logger.warning(f"TopicDetailView.delete: topic {topic_id} not found")
        raise Http404("Topic not found")


# =============================================================================
# FLASHCARD SET VIEWS
# =============================================================================

class FlashcardSetListView(ServiceMixin, APIView):
    """List all flashcard sets or create a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"FlashcardSetListView.get: user_id={request.user.id}, email={request.user.email}")
        topic_id = request.query_params.get('topic_id')
        sets = self.flashcard_set_service.list_sets(topic_id=int(topic_id) if topic_id else None)
        logger.debug(f"FlashcardSetListView.get: returning {len(sets)} sets")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = FlashcardSetSerializer(sets, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"FlashcardSetListView.post: user_id={request.user.id}, email={request.user.email}")
        if not request.user.can_manage_content():
            logger.warning(f"FlashcardSetListView.post: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = FlashcardSetSerializer(data=request.data)
        if serializer.is_valid():
            fc_set = self.flashcard_set_service.create_set(**serializer.validated_data)
            return Response(FlashcardSetSerializer(fc_set).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlashcardSetDetailView(ServiceMixin, APIView):
    """Retrieve, update, or delete a flashcard set."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        logger.debug(f"FlashcardSetDetailView.get: user_id={request.user.id}, set_id={set_id}")
        fc_set = self.flashcard_set_service.get_set(set_id)
        if not fc_set:
            logger.warning(f"FlashcardSetDetailView.get: set {set_id} not found")
            raise Http404("Flashcard set not found")
        # Check premium access for detail view
        if fc_set.is_premium and not self.can_access_premium(request):
            logger.warning(f"FlashcardSetDetailView.get: premium denied for user_id={request.user.id}, set_id={set_id}")
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = FlashcardSetDetailSerializer(fc_set)
        return Response(serializer.data)

    def put(self, request, set_id):
        logger.info(f"FlashcardSetDetailView.put: user_id={request.user.id}, set_id={set_id}")
        if not request.user.can_manage_content():
            logger.warning(f"FlashcardSetDetailView.put: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        fc_set = self.flashcard_set_service.get_set(set_id)
        if not fc_set:
            logger.warning(f"FlashcardSetDetailView.put: set {set_id} not found")
            raise Http404("Flashcard set not found")
        
        serializer = FlashcardSetSerializer(fc_set, data=request.data, partial=True)
        if serializer.is_valid():
            updated_set = self.flashcard_set_service.update_set(set_id, **serializer.validated_data)
            logger.info(f"FlashcardSetDetailView.put: set {set_id} updated")
            return Response(FlashcardSetSerializer(updated_set).data)
        logger.warning(f"FlashcardSetDetailView.put: validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, set_id):
        logger.info(f"FlashcardSetDetailView.delete: user_id={request.user.id}, set_id={set_id}")
        if not request.user.can_manage_content():
            logger.warning(f"FlashcardSetDetailView.delete: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.flashcard_set_service.delete_set(set_id):
            logger.info(f"FlashcardSetDetailView.delete: set {set_id} deleted")
            return Response({'message': 'Flashcard set deleted'}, status=status.HTTP_204_NO_CONTENT)
        logger.warning(f"FlashcardSetDetailView.delete: set {set_id} not found")
        raise Http404("Flashcard set not found")


# =============================================================================
# FLASHCARD VIEWS
# =============================================================================

class FlashcardListView(ServiceMixin, APIView):
    """List all flashcards or create a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"FlashcardListView.get: user_id={request.user.id}, email={request.user.email}")
        set_id = request.query_params.get('set_id')
        cards = self.flashcard_service.list_cards(set_id=int(set_id) if set_id else None)
        logger.debug(f"FlashcardListView.get: returning {len(cards)} cards")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = FlashcardListSerializer(cards, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"FlashcardListView.post: user_id={request.user.id}, email={request.user.email}")
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = FlashcardSerializer(data=request.data)
        if serializer.is_valid():
            card = self.flashcard_service.create_card(**serializer.validated_data)
            return Response(FlashcardSerializer(card).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FlashcardDetailView(ServiceMixin, APIView):
    """Retrieve, update, or delete a flashcard."""
    permission_classes = [IsAuthenticated]

    def get(self, request, card_id):
        logger.debug(f"FlashcardDetailView.get: user_id={request.user.id}, card_id={card_id}")
        card = self.flashcard_service.get_card(card_id)
        if not card:
            logger.warning(f"FlashcardDetailView.get: card {card_id} not found")
            raise Http404("Flashcard not found")
        # Check premium access for detail view
        if card.is_premium and not self.can_access_premium(request):
            logger.warning(f"FlashcardDetailView.get: premium denied for user_id={request.user.id}, card_id={card_id}")
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = FlashcardSerializer(card)
        return Response(serializer.data)

    def put(self, request, card_id):
        logger.info(f"FlashcardDetailView.put: user_id={request.user.id}, card_id={card_id}")
        if not request.user.can_manage_content():
            logger.warning(f"FlashcardDetailView.put: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        card = self.flashcard_service.get_card(card_id)
        if not card:
            logger.warning(f"FlashcardDetailView.put: card {card_id} not found")
            raise Http404("Flashcard not found")
        
        serializer = FlashcardSerializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            updated_card = self.flashcard_service.update_card(card_id, **serializer.validated_data)
            logger.info(f"FlashcardDetailView.put: card {card_id} updated")
            return Response(FlashcardSerializer(updated_card).data)
        logger.warning(f"FlashcardDetailView.put: validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, card_id):
        logger.info(f"FlashcardDetailView.delete: user_id={request.user.id}, card_id={card_id}")
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.flashcard_service.delete_card(card_id):
            return Response({'message': 'Flashcard deleted'}, status=status.HTTP_204_NO_CONTENT)
        raise Http404("Flashcard not found")


class FlashcardRandomView(ServiceMixin, APIView):
    """Get random flashcards from a set (for study mode)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        logger.debug(f"FlashcardRandomView.get: user_id={request.user.id}, set_id={set_id}")
        count = int(request.query_params.get('count', 10))
        cards = self.flashcard_service.get_random_cards(set_id, count)
        logger.debug(f"FlashcardRandomView.get: returning {len(cards)} random cards")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = FlashcardListSerializer(cards, many=True)
        return Response(serializer.data)


# =============================================================================
# MCQ SET VIEWS
# =============================================================================

class MCQSetListView(ServiceMixin, APIView):
    """List all MCQ sets or create a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"MCQSetListView.get: user_id={request.user.id}, email={request.user.email}")
        topic_id = request.query_params.get('topic_id')
        sets = self.mcq_set_service.list_sets(topic_id=int(topic_id) if topic_id else None)
        logger.debug(f"MCQSetListView.get: returning {len(sets)} sets")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQSetSerializer(sets, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"MCQSetListView.post: user_id={request.user.id}, email={request.user.email}")
        if not request.user.can_manage_content():
            logger.warning(f"MCQSetListView.post: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MCQSetSerializer(data=request.data)
        if serializer.is_valid():
            mcq_set = self.mcq_set_service.create_set(**serializer.validated_data)
            return Response(MCQSetSerializer(mcq_set).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MCQSetDetailView(ServiceMixin, APIView):
    """Retrieve, update, or delete an MCQ set."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        logger.debug(f"MCQSetDetailView.get: user_id={request.user.id}, set_id={set_id}")
        mcq_set = self.mcq_set_service.get_set(set_id)
        if not mcq_set:
            logger.warning(f"MCQSetDetailView.get: set {set_id} not found")
            raise Http404("MCQ set not found")
        # Check premium access for detail view
        if mcq_set.is_premium and not self.can_access_premium(request):
            logger.warning(f"MCQSetDetailView.get: premium denied for user_id={request.user.id}, set_id={set_id}")
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = MCQSetDetailSerializer(mcq_set)
        return Response(serializer.data)

    def put(self, request, set_id):
        logger.info(f"MCQSetDetailView.put: user_id={request.user.id}, set_id={set_id}")
        if not request.user.can_manage_content():
            logger.warning(f"MCQSetDetailView.put: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        mcq_set = self.mcq_set_service.get_set(set_id)
        if not mcq_set:
            logger.warning(f"MCQSetDetailView.put: set {set_id} not found")
            raise Http404("MCQ set not found")
        
        serializer = MCQSetSerializer(mcq_set, data=request.data, partial=True)
        if serializer.is_valid():
            updated_set = self.mcq_set_service.update_set(set_id, **serializer.validated_data)
            logger.info(f"MCQSetDetailView.put: set {set_id} updated")
            return Response(MCQSetSerializer(updated_set).data)
        logger.warning(f"MCQSetDetailView.put: validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, set_id):
        logger.info(f"MCQSetDetailView.delete: user_id={request.user.id}, set_id={set_id}")
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.mcq_set_service.delete_set(set_id):
            return Response({'message': 'MCQ set deleted'}, status=status.HTTP_204_NO_CONTENT)
        raise Http404("MCQ set not found")


# =============================================================================
# MCQ VIEWS
# =============================================================================

class MCQListView(ServiceMixin, APIView):
    """List all MCQs or create a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"MCQListView.get: user_id={request.user.id}, email={request.user.email}")
        set_id = request.query_params.get('set_id')
        mcqs = self.mcq_service.list_mcqs(set_id=int(set_id) if set_id else None)
        logger.debug(f"MCQListView.get: returning {len(mcqs)} MCQs")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQListSerializer(mcqs, many=True)
        return Response(serializer.data)

    def post(self, request):
        logger.info(f"MCQListView.post: user_id={request.user.id}, email={request.user.email}")
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MCQSerializer(data=request.data)
        if serializer.is_valid():
            mcq = self.mcq_service.create_mcq(**serializer.validated_data)
            return Response(MCQSerializer(mcq).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MCQDetailView(ServiceMixin, APIView):
    """Retrieve, update, or delete an MCQ."""
    permission_classes = [IsAuthenticated]

    def get(self, request, mcq_id):
        logger.debug(f"MCQDetailView.get: user_id={request.user.id}, mcq_id={mcq_id}")
        mcq = self.mcq_service.get_mcq(mcq_id)
        if not mcq:
            logger.warning(f"MCQDetailView.get: MCQ {mcq_id} not found")
            raise Http404("MCQ not found")
        # Check premium access for detail view
        if mcq.is_premium and not self.can_access_premium(request):
            logger.warning(f"MCQDetailView.get: premium denied for user_id={request.user.id}, mcq_id={mcq_id}")
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = MCQSerializer(mcq)
        return Response(serializer.data)

    def put(self, request, mcq_id):
        logger.info(f"MCQDetailView.put: user_id={request.user.id}, mcq_id={mcq_id}")
        if not request.user.can_manage_content():
            logger.warning(f"MCQDetailView.put: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        mcq = self.mcq_service.get_mcq(mcq_id)
        if not mcq:
            logger.warning(f"MCQDetailView.put: MCQ {mcq_id} not found")
            raise Http404("MCQ not found")
        
        serializer = MCQSerializer(mcq, data=request.data, partial=True)
        if serializer.is_valid():
            updated_mcq = self.mcq_service.update_mcq(mcq_id, **serializer.validated_data)
            logger.info(f"MCQDetailView.put: MCQ {mcq_id} updated")
            return Response(MCQSerializer(updated_mcq).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, mcq_id):
        logger.info(f"MCQDetailView.delete: user_id={request.user.id}, mcq_id={mcq_id}")
        if not request.user.can_manage_content():
            logger.warning(f"MCQDetailView.delete: permission denied for user_id={request.user.id}")
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.mcq_service.delete_mcq(mcq_id):
            logger.info(f"MCQDetailView.delete: MCQ {mcq_id} deleted")
            return Response({'message': 'MCQ deleted'}, status=status.HTTP_204_NO_CONTENT)
        logger.warning(f"MCQDetailView.delete: MCQ {mcq_id} not found")
        raise Http404("MCQ not found")


class MCQQuizView(ServiceMixin, APIView):
    """Get MCQs for quiz mode (without correct answers)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        logger.debug(f"MCQQuizView.get: user_id={request.user.id}, set_id={set_id}")
        count = int(request.query_params.get('count', 10))
        mcqs = self.mcq_service.get_random_mcqs(set_id, count)
        logger.debug(f"MCQQuizView.get: returning {len(mcqs)} quiz MCQs")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQPublicSerializer(mcqs, many=True)
        return Response(serializer.data)


class MCQCheckAnswerView(ServiceMixin, APIView):
    """Check user's answer for an MCQ."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.debug(f"MCQCheckAnswerView.post: user_id={request.user.id}, email={request.user.email}")
        serializer = MCQAnswerSerializer(data=request.data)
        if serializer.is_valid():
            mcq_id = serializer.validated_data['mcq_id']
            # Check premium access for this MCQ
            mcq = self.mcq_service.get_mcq(mcq_id)
            if mcq and mcq.is_premium and not self.can_access_premium(request):
                logger.warning(f"MCQCheckAnswerView.post: premium denied for user_id={request.user.id}, mcq_id={mcq_id}")
                return Response({'error': 'Premium content. Upgrade to access.'}, 
                               status=status.HTTP_403_FORBIDDEN)
            user_answer = serializer.validated_data['user_answer']
            result = self.mcq_service.check_answer(mcq_id, user_answer)
            logger.info(f"MCQCheckAnswerView.post: mcq_id={mcq_id}, user_answer={user_answer}, correct={result.get('correct')}")
            return Response(result)
        logger.warning(f"MCQCheckAnswerView.post: validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MCQRandomView(ServiceMixin, APIView):
    """Get random MCQs from a set (for study mode)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        logger.debug(f"MCQRandomView.get: user_id={request.user.id}, set_id={set_id}")
        count = int(request.query_params.get('count', 10))
        mcqs = self.mcq_service.get_random_mcqs(set_id, count)
        logger.debug(f"MCQRandomView.get: returning {len(mcqs)} random MCQs")
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQListSerializer(mcqs, many=True)
        return Response(serializer.data)


# =============================================================================
# PRACTICE VIEWS - Spaced Repetition Practice
# =============================================================================

class PracticeFlashcardsView(ServiceMixin, APIView):
    """Get flashcards for practice based on ease factor (SRS)."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('count', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of cards (default 10)'),
        ],
    )
    def get(self, request):
        logger.debug(f"PracticeFlashcardsView.get: user_id={request.user.id}, email={request.user.email}")
        from app.services.practice_service import PracticeService
        count = int(request.query_params.get('count', 10))
        service = PracticeService(request.user)
        cards = service.get_practice_flashcards(count)
        return Response({
            'count': len(cards),
            'questions': cards,
        })


class PracticeMCQsView(ServiceMixin, APIView):
    """Get MCQs for practice based on ease factor (SRS)."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('count', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of questions (default 10)'),
        ],
    )
    def get(self, request):
        logger.debug(f"PracticeMCQsView.get: user_id={request.user.id}, email={request.user.email}")
        from app.services.practice_service import PracticeService
        count = int(request.query_params.get('count', 10))
        service = PracticeService(request.user)
        mcqs = service.get_practice_mcqs(count)
        return Response({
            'count': len(mcqs),
            'questions': mcqs,
        })


class PracticeMixedView(ServiceMixin, APIView):
    """Get mixed flashcards and MCQs for practice based on ease factor."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('count', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, description='Number of questions (default 10)'),
        ],
    )
    def get(self, request):
        logger.debug(f"PracticeMixedView.get: user_id={request.user.id}, email={request.user.email}")
        from app.services.practice_service import PracticeService
        count = int(request.query_params.get('count', 10))
        service = PracticeService(request.user)
        questions = service.get_practice_mixed(count)
        return Response({
            'count': len(questions),
            'questions': questions,
        })


class PracticeSubmitFlashcardView(ServiceMixin, APIView):
    """Submit a rating for a flashcard (SRS update)."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['flashcard_id'],
            properties={
                'flashcard_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the flashcard'),
                'rating': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['again', 'hard', 'good', 'easy'],
                    description='Your rating: again (forgot), hard (struggled), good (recalled), easy (knew it)',
                    default='good'
                ),
            },
        ),
        responses={200: 'SRS updated successfully'},
    )
    def post(self, request):
        logger.info(f"PracticeSubmitFlashcardView.post: user_id={request.user.id}, email={request.user.email}")
        from app.services.practice_service import PracticeService
        flashcard_id = request.data.get('flashcard_id')
        rating = request.data.get('rating', 'good')

        if not flashcard_id:
            logger.warning(f"PracticeSubmitFlashcardView.post: flashcard_id required")
            return Response({'error': 'flashcard_id required'}, status=status.HTTP_400_BAD_REQUEST)

        service = PracticeService(request.user)
        result = service.submit_flashcard_rating(int(flashcard_id), rating)

        if 'error' in result:
            logger.warning(f"PracticeSubmitFlashcardView.post: error - {result['error']}")
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"PracticeSubmitFlashcardView.post: success for flashcard {flashcard_id}")
        return Response(result)


class PracticeSubmitMCQView(ServiceMixin, APIView):
    """Submit a rating for an MCQ (SRS update)."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['mcq_id', 'user_answer'],
            properties={
                'mcq_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the MCQ'),
                'user_answer': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['A', 'B', 'C', 'D'],
                    description='Your answer (A/B/C/D). System auto-checks correctness and updates SRS.'
                ),
            },
        ),
        responses={200: 'Answer checked, SRS updated automatically'},
    )
    def post(self, request):
        logger.info(f"PracticeSubmitMCQView.post: user_id={request.user.id}, email={request.user.email}")
        from app.services.practice_service import PracticeService
        mcq_id = request.data.get('mcq_id')
        user_answer = request.data.get('user_answer')

        if not mcq_id:
            logger.warning(f"PracticeSubmitMCQView.post: mcq_id required")
            return Response({'error': 'mcq_id required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_answer:
            logger.warning(f"PracticeSubmitMCQView.post: user_answer required")
            return Response({'error': 'user_answer required (A/B/C/D)'}, status=status.HTTP_400_BAD_REQUEST)

        service = PracticeService(request.user)
        result = service.submit_mcq_answer(int(mcq_id), user_answer)

        if 'error' in result:
            logger.warning(f"PracticeSubmitMCQView.post: error - {result['error']}")
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        logger.info(f"PracticeSubmitMCQView.post: success for mcq {mcq_id}, correct={result.get('is_correct')}")
        return Response(result)


# =============================================================================
# LEADERBOARD VIEWS
# =============================================================================

class LeaderboardView(ServiceMixin, APIView):
    """Get the combined leaderboard (MCQ-centric scoring)."""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('period', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                              description='Time period: weekly, monthly, yearly, all_time', default='all_time'),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER,
                              description='Max users to return', default=100),
        ],
        responses={200: 'Leaderboard ranking list'},
    )
    def get(self, request):
        logger.debug(f"LeaderboardView.get: user_id={request.user.id}, email={request.user.email}")
        from app.services.leaderboard_service import LeaderboardService

        period = request.query_params.get('period', 'all_time')
        limit = int(request.query_params.get('limit', 100))

        valid_periods = ['weekly', 'monthly', 'yearly', 'all_time']
        if period not in valid_periods:
            logger.warning(f"LeaderboardView.get: invalid period '{period}'")
            return Response({'error': f'Invalid period. Use one of: {valid_periods}'},
                           status=status.HTTP_400_BAD_REQUEST)

        service = LeaderboardService()
        leaderboard = service.get_leaderboard(period=period, limit=limit)

        logger.info(f"LeaderboardView.get: returning {len(leaderboard)} entries (period={period})")
        return Response({
            'period': period,
            'count': len(leaderboard),
            'leaderboard': leaderboard,
        })


# =============================================================================
# GAMIFICATION VIEWS (XP, Level, Badges)
# =============================================================================

class UserGamificationView(ServiceMixin, APIView):
    """Get XP, Level, and Badges for the authenticated user (computed/derived)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"UserGamificationView.get: user_id={request.user.id}, email={request.user.email}")
        from app.services.gamification_service import GamificationService

        service = GamificationService()
        data = service.get_user_gamification(request.user.id)

        return Response(data)


class UserBadgesView(ServiceMixin, APIView):
    """Get all badges (earned and not earned) for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"UserBadgesView.get: user_id={request.user.id}")
        from app.services.gamification_service import GamificationService

        service = GamificationService()
        all_badges = service.get_all_badges(request.user.id)

        return Response({
            'count': len(all_badges),
            'earned': len([b for b in all_badges if b['earned']]),
            'badges': all_badges,
        })


# =============================================================================
# CREATOR FIELD VIEWS - Creator's Paid Content Packages
# =============================================================================

class CreatorFieldListView(ServiceMixin, APIView):
    """List all active creator fields (public)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"CreatorFieldListView.get: user_id={request.user.id}")
        from app.services.creator_field_service import CreatorFieldService

        service = CreatorFieldService()
        fields = service.list_fields(public_only=True)

        data = []
        for f in fields:
            data.append({
                'id': f.id,
                'name': f.name,
                'description': f.description,
                'price': str(f.price),
                'creator_id': f.creator_id,
                'creator_name': f.creator.full_name if f.creator else None,
                'flashcard_set_count': f.get_flashcard_set_count(),
                'mcq_set_count': f.get_mcq_set_count(),
            })

        return Response({'count': len(data), 'fields': data})


class CreatorFieldDetailView(ServiceMixin, APIView):
    """Get details of a creator field."""
    permission_classes = [IsAuthenticated]

    def get(self, request, field_id):
        logger.debug(f"CreatorFieldDetailView.get: user_id={request.user.id}, field_id={field_id}")
        from app.services.creator_field_service import CreatorFieldService

        service = CreatorFieldService()
        field = service.get_field(field_id)
        if not field:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if user has access (creator or purchaser)
        has_access = service.has_access(request.user, field)

        data = {
            'id': field.id,
            'name': field.name,
            'description': field.description,
            'price': str(field.price),
            'creator_id': field.creator_id,
            'creator_name': field.creator.full_name if field.creator else None,
            'flashcard_set_count': field.get_flashcard_set_count(),
            'mcq_set_count': field.get_mcq_set_count(),
            'has_access': has_access,
        }

        if has_access:
            # Show the actual sets
            from app.api.serializers.content_serializers import FlashcardSetSerializer, MCQSetSerializer
            flashcard_sets = field.flashcard_sets.filter(is_active=True)
            mcq_sets = field.mcq_sets.filter(is_active=True)
            data['flashcard_sets'] = FlashcardSetSerializer(flashcard_sets, many=True).data
            data['mcq_sets'] = MCQSetSerializer(mcq_sets, many=True).data

        return Response(data)


class CreatorFieldCreateView(ServiceMixin, APIView):
    """Create a new creator field (content creators only)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logger.info(f"CreatorFieldCreateView.post: user_id={request.user.id}, email={request.user.email}")
        
        if request.user.role != 'content_creator':
            return Response({'error': 'Only content creators can create fields'}, 
                           status=status.HTTP_403_FORBIDDEN)

        from app.services.creator_field_service import CreatorFieldService
        service = CreatorFieldService()

        name = request.data.get('name')
        if not name:
            return Response({'error': 'name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            field = service.create_field(
                creator=request.user,
                name=name,
                description=request.data.get('description', ''),
                price=Decimal(request.data.get('price', '0.00')),
                is_active=request.data.get('is_active', True),
            )
            return Response({
                'id': field.id,
                'name': field.name,
                'description': field.description,
                'price': str(field.price),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating field: {e}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CreatorFieldPurchaseView(ServiceMixin, APIView):
    """Purchase a creator field."""
    permission_classes = [IsAuthenticated]

    def post(self, request, field_id):
        logger.info(f"CreatorFieldPurchaseView.post: user_id={request.user.id}, field_id={field_id}")
        
        from app.services.creator_field_service import CreatorFieldService
        service = CreatorFieldService()

        field = service.get_field(field_id)
        if not field:
            return Response({'error': 'Field not found'}, status=status.HTTP_404_NOT_FOUND)

        if not field.is_active:
            return Response({'error': 'Field is not available'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if already purchased
        if service.has_access(request.user, field):
            return Response({'message': 'Already purchased or owner'}, status=status.HTTP_200_OK)

        try:
            purchase = service.purchase_field(request.user, field)
            return Response({
                'message': 'Purchase successful',
                'field_id': field.id,
                'amount_paid': str(purchase.amount_paid),
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MyCreatorFieldsView(ServiceMixin, APIView):
    """List fields created by the current user (content creator)."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"MyCreatorFieldsView.get: user_id={request.user.id}")
        
        if request.user.role != 'content_creator':
            return Response({'error': 'Only content creators have creator fields'}, 
                           status=status.HTTP_403_FORBIDDEN)

        from app.services.creator_field_service import CreatorFieldService
        service = CreatorFieldService()
        fields = service.get_creator_fields(request.user)

        data = []
        for f in fields:
            data.append({
                'id': f.id,
                'name': f.name,
                'description': f.description,
                'price': str(f.price),
                'is_active': f.is_active,
                'flashcard_set_count': f.get_flashcard_set_count(),
                'mcq_set_count': f.get_mcq_set_count(),
            })

        return Response({'count': len(data), 'fields': data})


class MyPurchasedFieldsView(ServiceMixin, APIView):
    """List fields purchased by the current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logger.debug(f"MyPurchasedFieldsView.get: user_id={request.user.id}")
        
        from app.services.creator_field_service import CreatorFieldService
        service = CreatorFieldService()
        purchases = service.get_user_purchases(request.user)

        data = []
        for p in purchases:
            f = p.creator_field
            data.append({
                'purchase_id': p.id,
                'field_id': f.id,
                'field_name': f.name,
                'creator_name': f.creator.full_name if f.creator else None,
                'purchased_at': p.purchased_at.isoformat(),
                'amount_paid': str(p.amount_paid),
            })

        return Response({'count': len(data), 'purchases': data})
