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
        topics = self.topic_service.list_topics()
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = TopicListSerializer(topics, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TopicSerializer(data=request.data)
        if serializer.is_valid():
            topic = self.topic_service.create_topic(**serializer.validated_data)
            return Response(TopicSerializer(topic).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TopicDetailView(ServiceMixin, APIView):
    """Retrieve, update, or delete a topic."""
    permission_classes = [IsAuthenticated]

    def get(self, request, topic_id):
        topic = self.topic_service.get_topic(topic_id)
        if not topic:
            raise Http404("Topic not found")
        # Check premium access
        if topic.is_premium and not self.can_access_premium(request):
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = TopicSerializer(topic)
        return Response(serializer.data)

    def put(self, request, topic_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        topic = self.topic_service.get_topic(topic_id)
        if not topic:
            raise Http404("Topic not found")
        
        serializer = TopicSerializer(topic, data=request.data, partial=True)
        if serializer.is_valid():
            updated_topic = self.topic_service.update_topic(topic_id, **serializer.validated_data)
            return Response(TopicSerializer(updated_topic).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, topic_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.topic_service.delete_topic(topic_id):
            return Response({'message': 'Topic deleted'}, status=status.HTTP_204_NO_CONTENT)
        raise Http404("Topic not found")


# =============================================================================
# FLASHCARD SET VIEWS
# =============================================================================

class FlashcardSetListView(ServiceMixin, APIView):
    """List all flashcard sets or create a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        topic_id = request.query_params.get('topic_id')
        sets = self.flashcard_set_service.list_sets(topic_id=int(topic_id) if topic_id else None)
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = FlashcardSetSerializer(sets, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.can_manage_content():
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
        fc_set = self.flashcard_set_service.get_set(set_id)
        if not fc_set:
            raise Http404("Flashcard set not found")
        # Check premium access for detail view
        if fc_set.is_premium and not self.can_access_premium(request):
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = FlashcardSetDetailSerializer(fc_set)
        return Response(serializer.data)

    def put(self, request, set_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        fc_set = self.flashcard_set_service.get_set(set_id)
        if not fc_set:
            raise Http404("Flashcard set not found")
        
        serializer = FlashcardSetSerializer(fc_set, data=request.data, partial=True)
        if serializer.is_valid():
            updated_set = self.flashcard_set_service.update_set(set_id, **serializer.validated_data)
            return Response(FlashcardSetSerializer(updated_set).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, set_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.flashcard_set_service.delete_set(set_id):
            return Response({'message': 'Flashcard set deleted'}, status=status.HTTP_204_NO_CONTENT)
        raise Http404("Flashcard set not found")


# =============================================================================
# FLASHCARD VIEWS
# =============================================================================

class FlashcardListView(ServiceMixin, APIView):
    """List all flashcards or create a new one."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        set_id = request.query_params.get('set_id')
        cards = self.flashcard_service.list_cards(set_id=int(set_id) if set_id else None)
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = FlashcardListSerializer(cards, many=True)
        return Response(serializer.data)

    def post(self, request):
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
        card = self.flashcard_service.get_card(card_id)
        if not card:
            raise Http404("Flashcard not found")
        # Check premium access for detail view
        if card.is_premium and not self.can_access_premium(request):
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = FlashcardSerializer(card)
        return Response(serializer.data)

    def put(self, request, card_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        card = self.flashcard_service.get_card(card_id)
        if not card:
            raise Http404("Flashcard not found")
        
        serializer = FlashcardSerializer(card, data=request.data, partial=True)
        if serializer.is_valid():
            updated_card = self.flashcard_service.update_card(card_id, **serializer.validated_data)
            return Response(FlashcardSerializer(updated_card).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, card_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.flashcard_service.delete_card(card_id):
            return Response({'message': 'Flashcard deleted'}, status=status.HTTP_204_NO_CONTENT)
        raise Http404("Flashcard not found")


class FlashcardRandomView(ServiceMixin, APIView):
    """Get random flashcards from a set (for study mode)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        count = int(request.query_params.get('count', 10))
        cards = self.flashcard_service.get_random_cards(set_id, count)
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
        topic_id = request.query_params.get('topic_id')
        sets = self.mcq_set_service.list_sets(topic_id=int(topic_id) if topic_id else None)
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQSetSerializer(sets, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.can_manage_content():
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
        mcq_set = self.mcq_set_service.get_set(set_id)
        if not mcq_set:
            raise Http404("MCQ set not found")
        # Check premium access for detail view
        if mcq_set.is_premium and not self.can_access_premium(request):
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = MCQSetDetailSerializer(mcq_set)
        return Response(serializer.data)

    def put(self, request, set_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        mcq_set = self.mcq_set_service.get_set(set_id)
        if not mcq_set:
            raise Http404("MCQ set not found")
        
        serializer = MCQSetSerializer(mcq_set, data=request.data, partial=True)
        if serializer.is_valid():
            updated_set = self.mcq_set_service.update_set(set_id, **serializer.validated_data)
            return Response(MCQSetSerializer(updated_set).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, set_id):
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
        set_id = request.query_params.get('set_id')
        mcqs = self.mcq_service.list_mcqs(set_id=int(set_id) if set_id else None)
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQListSerializer(mcqs, many=True)
        return Response(serializer.data)

    def post(self, request):
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
        mcq = self.mcq_service.get_mcq(mcq_id)
        if not mcq:
            raise Http404("MCQ not found")
        # Check premium access for detail view
        if mcq.is_premium and not self.can_access_premium(request):
            return Response({'error': 'Premium content. Upgrade to access.'}, 
                           status=status.HTTP_403_FORBIDDEN)
        serializer = MCQSerializer(mcq)
        return Response(serializer.data)

    def put(self, request, mcq_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        mcq = self.mcq_service.get_mcq(mcq_id)
        if not mcq:
            raise Http404("MCQ not found")
        
        serializer = MCQSerializer(mcq, data=request.data, partial=True)
        if serializer.is_valid():
            updated_mcq = self.mcq_service.update_mcq(mcq_id, **serializer.validated_data)
            return Response(MCQSerializer(updated_mcq).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, mcq_id):
        if not request.user.can_manage_content():
            return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        
        if self.mcq_service.delete_mcq(mcq_id):
            return Response({'message': 'MCQ deleted'}, status=status.HTTP_204_NO_CONTENT)
        raise Http404("MCQ not found")


class MCQQuizView(ServiceMixin, APIView):
    """Get MCQs for quiz mode (without correct answers)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        count = int(request.query_params.get('count', 10))
        mcqs = self.mcq_service.get_random_mcqs(set_id, count)
        # Don't filter - return all with is_premium flag so UI can blur
        serializer = MCQPublicSerializer(mcqs, many=True)
        return Response(serializer.data)


class MCQCheckAnswerView(ServiceMixin, APIView):
    """Check user's answer for an MCQ."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MCQAnswerSerializer(data=request.data)
        if serializer.is_valid():
            mcq_id = serializer.validated_data['mcq_id']
            # Check premium access for this MCQ
            mcq = self.mcq_service.get_mcq(mcq_id)
            if mcq and mcq.is_premium and not self.can_access_premium(request):
                return Response({'error': 'Premium content. Upgrade to access.'}, 
                               status=status.HTTP_403_FORBIDDEN)
            user_answer = serializer.validated_data['user_answer']
            result = self.mcq_service.check_answer(mcq_id, user_answer)
            return Response(result)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MCQRandomView(ServiceMixin, APIView):
    """Get random MCQs from a set (for study mode)."""
    permission_classes = [IsAuthenticated]

    def get(self, request, set_id):
        count = int(request.query_params.get('count', 10))
        mcqs = self.mcq_service.get_random_mcqs(set_id, count)
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
        from app.services.practice_service import PracticeService
        flashcard_id = request.data.get('flashcard_id')
        rating = request.data.get('rating', 'good')

        if not flashcard_id:
            return Response({'error': 'flashcard_id required'}, status=status.HTTP_400_BAD_REQUEST)

        service = PracticeService(request.user)
        result = service.submit_flashcard_rating(int(flashcard_id), rating)

        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
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
        from app.services.practice_service import PracticeService
        mcq_id = request.data.get('mcq_id')
        user_answer = request.data.get('user_answer')

        if not mcq_id:
            return Response({'error': 'mcq_id required'}, status=status.HTTP_400_BAD_REQUEST)
        if not user_answer:
            return Response({'error': 'user_answer required (A/B/C/D)'}, status=status.HTTP_400_BAD_REQUEST)

        service = PracticeService(request.user)
        result = service.submit_mcq_answer(int(mcq_id), user_answer)

        if 'error' in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
        return Response(result)
