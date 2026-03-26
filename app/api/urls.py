"""
API URLs - Main URL routing for the application.
N-layered architecture: API routing layer.
"""

from django.contrib import admin
from django.urls import path, re_path
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

# Import from new layer-based structure
from app.api.views.user_views import (
    FollowUserView, UnfollowUserView, UserFollowersView, UserFollowingView,
    CustomTokenObtainPairView,
    UserRegistrationView,
    UserProfileView,
    UserListView,
    UserDetailView,
    UserStatsView,
    ChangePasswordView,
    UserRoleManagementView,
)
from app.api.views.subscription_views import (
    UserSubscriptionView,
    SubscriptionCancelView,
    SubscriptionCheckPremiumView,
    AdminSubscriptionListView,
    AdminSubscriptionDetailView,
    AdminPremiumUsersView,
    AdminSubscriptionStatsView,
)
from app.api.views.content_views import (
    CreatorFieldListView, CreatorFieldDetailView, CreatorFieldCreateView, CreatorFieldPurchaseView,
    MyCreatorFieldsView, MyPurchasedFieldsView,
    TopicListView, TopicDetailView,
    FlashcardSetListView, FlashcardSetDetailView, FlashcardListView, FlashcardDetailView, FlashcardRandomView,
    MCQSetListView, MCQSetDetailView, MCQListView, MCQDetailView, MCQQuizView, MCQCheckAnswerView, MCQRandomView,
    PracticeFlashcardsView, PracticeMCQsView, PracticeMixedView,
    PracticeSubmitFlashcardView, PracticeSubmitMCQView,
    LeaderboardView,
    UserGamificationView,
    UserBadgesView,
)


# Swagger Schema View
schema_view = get_schema_view(
    openapi.Info(
        title="Language Learning App API",
        default_version='v1',
        description="""
## Language Learning App Backend API

This API provides endpoints for:
- **Authentication**: User registration, login, token management
- **Users**: User profile management, role-based access
- **Subscriptions**: Premium subscription management
- **Content**: Topics, Flashcards, and Multiple Choice Questions (MCQs)

### Content Structure:
- **Topics**: Categories for organizing learning content (e.g., Food & Dining, Travel)
- **Flashcard Sets**: Multiple sets per topic, each containing flashcards
- **Flashcards**: Front/back cards with audio, images, hints
- **MCQ Sets**: Multiple sets per topic, each containing MCQs
- **MCQs**: Multiple choice questions with 4 options

### User Roles:
- **Admin**: Full access to all resources
- **Content Creator**: Can manage content (topics, flashcards, MCQs)
- **User**: Regular user with basic access

### 🔐 Authentication:
Use JWT Bearer token for authenticated endpoints.

**When clicking "Authorize" button, enter your token in this EXACT format:**
```
Bearer <your_access_token>
```

Example:
```
Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

Get tokens from `/api/auth/login/`

> ⚠️ **Important**: The "Bearer " prefix is REQUIRED!
        """,
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="admin@languagelearning.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

# URL patterns
urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API Documentation (Swagger)
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Authentication
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/register/', UserRegistrationView.as_view(), name='user_register'),

    # User Profile
    path('api/users/profile/', UserProfileView.as_view(), name='user_profile'),
    path('api/users/change-password/', ChangePasswordView.as_view(), name='change_password'),

    # User Management (Admin)
    path('api/users/', UserListView.as_view(), name='user_list'),
    path('api/users/stats/', UserStatsView.as_view(), name='user_stats'),
    path('api/users/<int:user_id>/', UserDetailView.as_view(), name='user_detail'),
    path('api/users/<int:user_id>/follow/', FollowUserView.as_view(), name='follow_user'),
    path('api/users/<int:user_id>/unfollow/', UnfollowUserView.as_view(), name='unfollow_user'),
    path('api/users/<int:user_id>/followers/', UserFollowersView.as_view(), name='user_followers'),
    path('api/users/<int:user_id>/following/', UserFollowingView.as_view(), name='user_following'),
    path('api/users/<int:user_id>/role/<str:action>/', UserRoleManagementView.as_view(), name='user_role_management'),

    # Subscriptions
    path('api/subscriptions/', UserSubscriptionView.as_view(), name='user_subscription'),
    path('api/subscriptions/cancel/', SubscriptionCancelView.as_view(), name='subscription_cancel'),
    path('api/subscriptions/check-premium/', SubscriptionCheckPremiumView.as_view(), name='check_premium'),

    # Subscriptions (Admin)
    path('api/admin/subscriptions/', AdminSubscriptionListView.as_view(), name='admin_subscription_list'),
    path('api/admin/subscriptions/stats/', AdminSubscriptionStatsView.as_view(), name='admin_subscription_stats'),
    path('api/admin/subscriptions/premium-users/', AdminPremiumUsersView.as_view(), name='admin_premium_users'),
    path('api/admin/subscriptions/<int:subscription_id>/', AdminSubscriptionDetailView.as_view(), name='admin_subscription_detail'),

    # Content - Topics
    path('api/content/topics/', TopicListView.as_view(), name='topic_list'),
    path('api/content/topics/<int:topic_id>/', TopicDetailView.as_view(), name='topic_detail'),

    # Content - Flashcard Sets
    path('api/content/flashcard-sets/', FlashcardSetListView.as_view(), name='flashcard_set_list'),
    path('api/content/flashcard-sets/<int:set_id>/', FlashcardSetDetailView.as_view(), name='flashcard_set_detail'),

    # Content - Flashcards
    path('api/content/flashcards/', FlashcardListView.as_view(), name='flashcard_list'),
    path('api/content/flashcards/<int:card_id>/', FlashcardDetailView.as_view(), name='flashcard_detail'),
    path('api/content/flashcards/random/<int:set_id>/', FlashcardRandomView.as_view(), name='flashcard_random'),

    # Content - MCQ Sets
    path('api/content/mcq-sets/', MCQSetListView.as_view(), name='mcq_set_list'),
    path('api/content/mcq-sets/<int:set_id>/', MCQSetDetailView.as_view(), name='mcq_set_detail'),

    # Content - MCQs
    path('api/content/mcqs/', MCQListView.as_view(), name='mcq_list'),
    path('api/content/mcqs/<int:mcq_id>/', MCQDetailView.as_view(), name='mcq_detail'),
    path('api/content/mcqs/quiz/<int:set_id>/', MCQQuizView.as_view(), name='mcq_quiz'),
    path('api/content/mcqs/check-answer/', MCQCheckAnswerView.as_view(), name='mcq_check_answer'),
    path('api/content/mcqs/random/<int:set_id>/', MCQRandomView.as_view(), name='mcq_random'),

    # Practice (Spaced Repetition)
    path('api/practice/', PracticeMixedView.as_view(), name='practice_mixed'),
    path('api/practice/flashcards/', PracticeFlashcardsView.as_view(), name='practice_flashcards'),
    path('api/practice/mcqs/', PracticeMCQsView.as_view(), name='practice_mcqs'),
    path('api/practice/submit/flashcard/', PracticeSubmitFlashcardView.as_view(), name='practice_submit_flashcard'),
    path('api/practice/submit/mcq/', PracticeSubmitMCQView.as_view(), name='practice_submit_mcq'),

    # Leaderboard
    path('api/leaderboard/', LeaderboardView.as_view(), name='leaderboard'),

    # Gamification (XP, Level, Badges) - computed/derived, no storage
    path('api/gamification/', UserGamificationView.as_view(), name='gamification'),
    path('api/gamification/badges/', UserBadgesView.as_view(), name='gamification_badges'),

    # Creator Fields
    path('api/creator-fields/', CreatorFieldListView.as_view(), name='creator_field_list'),
    path('api/creator-fields/my/', MyCreatorFieldsView.as_view(), name='my_creator_fields'),
    path('api/creator-fields/purchased/', MyPurchasedFieldsView.as_view(), name='my_purchased_fields'),
    path('api/creator-fields/<int:field_id>/', CreatorFieldDetailView.as_view(), name='creator_field_detail'),
    path('api/creator-fields/create/', CreatorFieldCreateView.as_view(), name='creator_field_create'),
    path('api/creator-fields/<int:field_id>/purchase/', CreatorFieldPurchaseView.as_view(), name='creator_field_purchase'),

]
