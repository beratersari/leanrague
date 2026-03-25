"""
Models - All data models.
N-layered architecture: Data layer.
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    """Base model with created_at and updated_at fields."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        abstract = True


class UserRole(models.TextChoices):
    ADMIN = 'admin', 'Admin'
    CONTENT_CREATOR = 'content_creator', 'Content Creator'
    USER = 'user', 'User'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser, TimeStampedModel):
    username = None
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.USER, db_index=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    last_login_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        db_table = 'users_customuser'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email

    def can_manage_content(self):
        return self.role in [UserRole.ADMIN, UserRole.CONTENT_CREATOR]

    def can_access_premium_content(self):
        """Check if user can access premium content."""
        # Admin and Content Creators always have access
        if self.role in [UserRole.ADMIN, UserRole.CONTENT_CREATOR]:
            return True
        # Regular users need active premium subscription
        try:
            return self.subscription.can_access_premium_content()
        except:
            return False


class SubscriptionPlan(models.TextChoices):
    FREE = 'free', 'Free'
    BASIC = 'basic', 'Basic'
    PREMIUM = 'premium', 'Premium'
    ENTERPRISE = 'enterprise', 'Enterprise'


class SubscriptionStatus(models.TextChoices):
    ACTIVE = 'active', 'Active'
    EXPIRED = 'expired', 'Expired'
    CANCELLED = 'cancelled', 'Cancelled'
    PENDING = 'pending', 'Pending'


class Subscription(TimeStampedModel):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='subscription')
    plan = models.CharField(max_length=20, choices=SubscriptionPlan.choices, default=SubscriptionPlan.FREE, db_index=True)
    status = models.CharField(max_length=20, choices=SubscriptionStatus.choices, default=SubscriptionStatus.ACTIVE, db_index=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    auto_renew = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True, null=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    class Meta:
        db_table = 'subscriptions_subscription'
        verbose_name = 'Subscription'
        verbose_name_plural = 'Subscriptions'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.plan} ({self.status})"

    @property
    def is_premium(self):
        return self.plan != SubscriptionPlan.FREE and self.status == SubscriptionStatus.ACTIVE

    @property
    def days_remaining(self):
        if not self.end_date:
            return None
        remaining = (self.end_date - timezone.now()).days
        return max(0, remaining)

    def can_access_premium_content(self):
        return self.is_premium and self.status == SubscriptionStatus.ACTIVE


# =============================================================================
# CONTENT MODELS - Topic, Flashcard, MCQ
# =============================================================================

class Topic(TimeStampedModel):
    """
    Topic - A category for organizing learning content.
    Examples: Food & Dining, Travel, Business, Everyday Conversation
    """
    name = models.CharField(max_length=200, db_index=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True, help_text="Icon name or emoji")
    is_active = models.BooleanField(default=True, db_index=True)
    is_premium = models.BooleanField(default=False, db_index=True, help_text="Premium users only")
    order = models.IntegerField(default=0, help_text="Display order")

    class Meta:
        db_table = 'content_topic'
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name

    @property
    def flashcard_count(self):
        return Flashcard.objects.filter(flashcard_set__topic=self).count()

    @property
    def mcq_count(self):
        return MCQ.objects.filter(mcq_set__topic=self).count()


class FlashcardSet(TimeStampedModel):
    """
    FlashcardSet - A collection of flashcards under a topic.
    A topic can have multiple flashcard sets.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='flashcard_sets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_premium = models.BooleanField(default=False, db_index=True, help_text="Premium users only")
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'content_flashcard_set'
        verbose_name = 'Flashcard Set'
        verbose_name_plural = 'Flashcard Sets'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.topic.name} - {self.name}"


class Flashcard(TimeStampedModel):
    """
    Flashcard - A single flashcard with front and back content.
    """
    flashcard_set = models.ForeignKey(FlashcardSet, on_delete=models.CASCADE, related_name='flashcards')
    front = models.CharField(max_length=500, help_text="Question/word/prompt")
    back = models.CharField(max_length=500, help_text="Answer/translation/definition")
    front_audio = models.URLField(blank=True, null=True, help_text="Audio URL for front side")
    back_audio = models.URLField(blank=True, null=True, help_text="Audio URL for back side")
    image_url = models.URLField(blank=True, null=True)
    example_sentence = models.TextField(blank=True)
    hint = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_premium = models.BooleanField(default=False, db_index=True, help_text="Premium users only")
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'content_flashcard'
        verbose_name = 'Flashcard'
        verbose_name_plural = 'Flashcards'
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.front} → {self.back}"


class MCQSet(TimeStampedModel):
    """
    MCQSet - A collection of multiple choice questions under a topic.
    A topic can have multiple MCQ sets.
    """
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='mcq_sets')
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_premium = models.BooleanField(default=False, db_index=True, help_text="Premium users only")
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'content_mcq_set'
        verbose_name = 'MCQ Set'
        verbose_name_plural = 'MCQ Sets'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.topic.name} - {self.name}"


class MCQ(TimeStampedModel):
    """
    MCQ - A multiple choice question with 4 options.
    """
    mcq_set = models.ForeignKey(MCQSet, on_delete=models.CASCADE, related_name='mcqs')
    question = models.TextField(help_text="The question text")
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(max_length=1, choices=[
        ('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')
    ], default='A')
    explanation = models.TextField(blank=True, help_text="Explanation for the answer")
    audio_url = models.URLField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    hint = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    is_premium = models.BooleanField(default=False, db_index=True, help_text="Premium users only")
    order = models.IntegerField(default=0)

    class Meta:
        db_table = 'content_mcq'
        verbose_name = 'MCQ'
        verbose_name_plural = 'MCQs'
        ordering = ['order', 'id']

    def __str__(self):
        return f"Q: {self.question[:50]}..."

    @property
    def correct_answer(self):
        options = {'A': self.option_a, 'B': self.option_b, 'C': self.option_c, 'D': self.option_d}
        return options.get(self.correct_option)

    def check_answer(self, user_answer):
        return user_answer.upper() == self.correct_option.upper()


# =============================================================================
# USER PROGRESS MODELS - Spaced Repetition System (SRS)
# =============================================================================

class Rating(models.TextChoices):
    AGAIN = 'again', 'Again'
    HARD = 'hard', 'Hard'
    GOOD = 'good', 'Good'
    EASY = 'easy', 'Easy'


class UserFlashcardProgress(TimeStampedModel):
    """
    Tracks user's progress on a flashcard for spaced repetition.
    Each user has their own ease factor and review schedule per card.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='flashcard_progress')
    flashcard = models.ForeignKey(Flashcard, on_delete=models.CASCADE, related_name='user_progress')
    ease_factor = models.FloatField(default=2.5, help_text="SM-2 ease factor (1.3 - 2.5)")
    interval_days = models.IntegerField(default=1, help_text="Days until next review")
    next_review_date = models.DateField(null=True, blank=True, help_text="When to review next")
    last_rating = models.CharField(max_length=10, choices=Rating.choices, blank=True, null=True)
    times_seen = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    last_studied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'progress_flashcard'
        verbose_name = 'Flashcard Progress'
        verbose_name_plural = 'Flashcard Progress'
        unique_together = ('user', 'flashcard')
        ordering = ['next_review_date', '-created_at']

    def __str__(self):
        return f"{self.user.email} - {self.flashcard.front[:20]} (EF: {self.ease_factor:.2f})"

    def update_srs(self, rating: str):
        """Update ease factor and interval based on SM-2 algorithm."""
        from datetime import timedelta
        from django.utils import timezone

        self.times_seen += 1
        if rating in ['good', 'easy']:
            self.times_correct += 1

        self.last_rating = rating
        self.last_studied_at = timezone.now()

        # SM-2 Algorithm
        if rating == 'again':
            self.interval_days = 1
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
            # "Again" = failed, show again TODAY (immediate re-study)
            self.next_review_date = timezone.now().date()
        elif rating == 'hard':
            self.interval_days = max(1, self.interval_days)
            self.ease_factor = max(1.3, self.ease_factor - 0.15)
            self.next_review_date = (timezone.now() + timedelta(days=self.interval_days)).date()
        elif rating == 'good':
            if self.times_seen == 1:
                self.interval_days = 1
            elif self.times_seen == 2:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor)
            self.next_review_date = (timezone.now() + timedelta(days=self.interval_days)).date()
        elif rating == 'easy':
            if self.times_seen == 1:
                self.interval_days = 4
            elif self.times_seen == 2:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor * 1.3)
            self.next_review_date = (timezone.now() + timedelta(days=self.interval_days)).date()

        self.ease_factor = min(2.5, max(1.3, self.ease_factor))
        self.save()

    @property
    def is_due(self):
        from django.utils import timezone
        if not self.next_review_date:
            return True
        return self.next_review_date <= timezone.now().date()


class UserMCQProgress(TimeStampedModel):
    """
    Tracks user's progress on an MCQ for spaced repetition.
    Each user has their own ease factor and review schedule per question.
    """
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='mcq_progress')
    mcq = models.ForeignKey(MCQ, on_delete=models.CASCADE, related_name='user_progress')
    ease_factor = models.FloatField(default=2.5, help_text="SM-2 ease factor (1.3 - 2.5)")
    interval_days = models.IntegerField(default=1, help_text="Days until next review")
    next_review_date = models.DateField(null=True, blank=True, help_text="When to review next")
    last_rating = models.CharField(max_length=10, choices=Rating.choices, blank=True, null=True)
    times_seen = models.IntegerField(default=0)
    times_correct = models.IntegerField(default=0)
    last_studied_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'progress_mcq'
        verbose_name = 'MCQ Progress'
        verbose_name_plural = 'MCQ Progress'
        unique_together = ('user', 'mcq')
        ordering = ['next_review_date', '-created_at']

    def __str__(self):
        return f"{self.user.email} - MCQ {self.mcq.id} (EF: {self.ease_factor:.2f})"

    def update_srs(self, rating: str):
        """Update ease factor and interval based on SM-2 algorithm."""
        from datetime import timedelta
        from django.utils import timezone

        self.times_seen += 1
        if rating in ['good', 'easy']:
            self.times_correct += 1

        self.last_rating = rating
        self.last_studied_at = timezone.now()

        # SM-2 Algorithm
        if rating == 'again':
            self.interval_days = 1
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
            # "Again" = failed, show again TODAY (immediate re-study)
            self.next_review_date = timezone.now().date()
        elif rating == 'hard':
            self.interval_days = max(1, self.interval_days)
            self.ease_factor = max(1.3, self.ease_factor - 0.15)
            self.next_review_date = (timezone.now() + timedelta(days=self.interval_days)).date()
        elif rating == 'good':
            if self.times_seen == 1:
                self.interval_days = 1
            elif self.times_seen == 2:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor)
            self.next_review_date = (timezone.now() + timedelta(days=self.interval_days)).date()
        elif rating == 'easy':
            if self.times_seen == 1:
                self.interval_days = 4
            elif self.times_seen == 2:
                self.interval_days = 6
            else:
                self.interval_days = int(self.interval_days * self.ease_factor * 1.3)
            self.next_review_date = (timezone.now() + timedelta(days=self.interval_days)).date()

        self.ease_factor = min(2.5, max(1.3, self.ease_factor))
        self.save()

    @property
    def is_due(self):
        from django.utils import timezone
        if not self.next_review_date:
            return True
        return self.next_review_date <= timezone.now().date()
