# Language Learning App - Backend

A Django-based backend for a Language Learning Application with n-layered architecture.

## 🏗️ Architecture

This project follows **n-layered architecture** pattern for clean separation of concerns:

```
app/
├── api/                          # API Layer (Presentation)
│   ├── urls.py                   # URL routing
│   ├── views/
│   │   ├── user_views.py         # User profile, auth, management
│   │   ├── subscription_views.py # Subscription CRUD & admin
│   │   └── content_views.py      # Topics, Flashcards, MCQs, Practice, Leaderboard, Gamification
│   └── serializers/
│       ├── user_serializers.py
│       ├── subscription_serializers.py
│       └── content_serializers.py
├── services/                     # Business Logic Layer
│   ├── user_service.py
│   ├── subscription_service.py
│   ├── topic_service.py
│   ├── flashcard_service.py
│   ├── mcq_service.py
│   ├── practice_service.py       # SRS practice logic
│   ├── leaderboard_service.py    # Leaderboard scoring (MCQ-centric)
│   └── gamification_service.py   # XP, Levels, Badges (computed)
├── repositories/                 # Data Access Layer (static methods)
│   ├── user_repository.py
│   ├── subscription_repository.py
│   ├── topic_repository.py
│   ├── flashcard_repository.py
│   └── mcq_repository.py
├── models/                       # Data Layer
│   ├── models.py                 # All models
│   └── migrations/
├── core/
│   ├── logger.py                 # Configurable logging utility
│   ├── exceptions.py
│   └── models.py                 # TimeStampedModel base
├── authentication/               # JWT Authentication
├── permissions/                  # Role-based access control
└── config/                       # Settings, ASGI, WSGI
```

## 👥 User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | Full system access | Manage all users, subscriptions, content |
| **Content Creator** | Content management | Create and manage learning content |
| **User** | Regular user | Access learning materials, manage own profile, practice |

## ✨ Features

- ✅ **Authentication**: JWT-based (access + refresh tokens)
- ✅ **User Management**: Profile, password change, admin CRUD, role management
- ✅ **Subscriptions**: Free/Basic/Premium/Enterprise plans, premium content gating
- ✅ **Content**: Topics → FlashcardSets → Flashcards, MCQSets → MCQs
- ✅ **Practice (SRS)**: Spaced repetition for flashcards & MCQs with ease factors
- ✅ **Leaderboard**: Combined MCQ-centric scoring (weekly/monthly/yearly/all-time)
- ✅ **Gamification**: XP, Levels, Badges (computed/derived — no extra storage)
- ✅ **Logging**: Configurable logger with DEBUG/INFO/WARNING/ERROR/CRITICAL levels
- ✅ **Role-based Access Control**: Permission classes (IsAdmin, IsContentCreator)
- ✅ **Swagger Documentation**: Interactive API docs via drf-yasg
- ✅ **SQLite3**: Development DB (easily migrate to PostgreSQL)

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

```bash
git clone <repository-url>
cd lang_learn
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Open **http://localhost:8000/swagger/** for API docs.

### 🧪 Test Admin

| Field | Value |
|-------|-------|
| Email | `admin@languagelearning.com` |
| Password | `Admin123!@#` |

Reset:
```bash
python manage.py create_test_admin
```

### 🎭 Load Mock Data

```bash
# Load users, topics, content
python manage.py load_mock_data

# Generate SRS progress for all users (optional: --leaderboard for varied dates & set completions)
python manage.py generate_mock_submissions --leaderboard
```

Mock users:
| Email | Password | Role | Subscription |
|-------|----------|------|--------------|
| `admin@test.com` | `Admin123!` | Admin | — |
| `creator1@test.com` | `Creator123!` | Content Creator | Basic |
| `creator2@test.com` | `Creator123!` | Content Creator | Free |
| `user1@test.com` | `User123!` | User | Premium (1yr) |
| `user2@test.com` | `User123!` | User | Premium (30d) |
| `user3@test.com` | `User123!` | User | Basic (90d) |
| `user4@test.com` | `User123!` | User | Free |
| `user5@test.com` | `User123!` | User | Free |

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login → tokens + user | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |

### Users

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET/PUT/PATCH | `/api/users/profile/` | Own profile | Yes |
| POST | `/api/users/change-password/` | Change password | Yes |
| GET | `/api/users/` | List all (Admin) | Admin |
| POST | `/api/users/` | Create user (Admin) | Admin |
| GET | `/api/users/<id>/` | User details (Admin) | Admin |
| PUT/PATCH | `/api/users/<id>/` | Update user (Admin) | Admin |
| DELETE | `/api/users/<id>/` | Delete user (Admin) | Admin |
| GET | `/api/users/stats/` | User statistics (Admin) | Admin |
| POST | `/api/users/<id>/role/<action>/` | Grant/revoke role (Admin) | Admin |

### Subscriptions

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/subscriptions/` | My subscription | Yes |
| POST | `/api/subscriptions/` | Create/upgrade | Yes |
| POST | `/api/subscriptions/cancel/` | Cancel | Yes |
| GET | `/api/subscriptions/check-premium/` | Check premium access | Yes |
| GET | `/api/admin/subscriptions/` | All subs (Admin) | Admin |
| GET | `/api/admin/subscriptions/stats/` | Stats (Admin) | Admin |
| GET | `/api/admin/subscriptions/premium-users/` | Premium users (Admin) | Admin |

### Content — Topics

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/content/topics/` | List topics | Yes |
| POST | `/api/content/topics/` | Create (Admin/Creator) | Yes |
| GET | `/api/content/topics/<id>/` | Details | Yes |
| PUT/PATCH | `/api/content/topics/<id>/` | Update | Yes |
| DELETE | `/api/content/topics/<id>/` | Delete | Yes |

### Content — Flashcard Sets

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/content/flashcard-sets/` | List (?topic_id=) | Yes |
| POST | `/api/content/flashcard-sets/` | Create | Yes |
| GET | `/api/content/flashcard-sets/<id>/` | Details with cards | Yes |
| PUT/PATCH | `/api/content/flashcard-sets/<id>/` | Update | Yes |
| DELETE | `/api/content/flashcard-sets/<id>/` | Delete | Yes |

### Content — Flashcards

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/content/flashcards/` | List (?set_id=) | Yes |
| POST | `/api/content/flashcards/` | Create | Yes |
| GET | `/api/content/flashcards/<id>/` | Details | Yes |
| PUT/PATCH | `/api/content/flashcards/<id>/` | Update | Yes |
| DELETE | `/api/content/flashcards/<id>/` | Delete | Yes |
| GET | `/api/content/flashcards/random/<set_id>/?count=10` | Random for study | Yes |

### Content — MCQ Sets

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/content/mcq-sets/` | List (?topic_id=) | Yes |
| POST | `/api/content/mcq-sets/` | Create | Yes |
| GET | `/api/content/mcq-sets/<id>/` | Details with MCQs | Yes |
| PUT/PATCH | `/api/content/mcq-sets/<id>/` | Update | Yes |
| DELETE | `/api/content/mcq-sets/<id>/` | Delete | Yes |

### Content — MCQs

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/content/mcqs/` | List (?set_id=) | Yes |
| POST | `/api/content/mcqs/` | Create | Yes |
| GET | `/api/content/mcqs/<id>/` | Details | Yes |
| PUT/PATCH | `/api/content/mcqs/<id>/` | Update | Yes |
| DELETE | `/api/content/mcqs/<id>/` | Delete | Yes |
| GET | `/api/content/mcqs/quiz/<set_id>/?count=10` | Quiz (no answers) | Yes |
| POST | `/api/content/mcqs/check-answer/` | Check: `{"mcq_id":1,"user_answer":"A"}` | Yes |
| GET | `/api/content/mcqs/random/<set_id>/?count=10` | Random for study | Yes |

### Practice (Spaced Repetition)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/practice/` | Mixed flashcards + MCQs (SRS-sorted) | Yes |
| GET | `/api/practice/flashcards/` | Due flashcards | Yes |
| GET | `/api/practice/mcqs/` | Due MCQs | Yes |
| POST | `/api/practice/submit/flashcard/` | Rate: `{"flashcard_id":1,"rating":"good\|hard\|easy\|again"}` | Yes |
| POST | `/api/practice/submit/mcq/` | Answer: `{"mcq_id":1,"user_answer":"A"}` (auto-SRS) | Yes |

### Leaderboard (MCQ-centric)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/leaderboard/?period=monthly&limit=100` | Ranked users | Yes |

**Periods**: `weekly`, `monthly`, `yearly`, `all_time`

**Scoring**: `(unique MCQs correct × 10) + (MCQ sets × 50) + (Flashcard sets × 30)`

### Gamification (XP, Levels, Badges)

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/gamification/` | XP, Level, progress, earned badges | Yes |
| GET | `/api/gamification/badges/` | All badges (earned + unearned) | Yes |

**XP Formula**: `(unique MCQs × 10) + (MCQ sets × 25) + (Flashcard sets × 15)`  
**Level**: `1 + XP // 100` (100 XP per level)  
**Badges**: 8 computed badges (e.g., First Steps, Quiz Master, Set Starter, etc.)

## 🔐 Authentication

Login returns tokens + user:

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"pass"}'
```

```json
{"access":"...","refresh":"...","user":{"id":1,"email":"...","role":"user",...}}
```

Use: `Authorization: Bearer <access_token>`

## 🗄️ Database

- **Dev**: SQLite3 (`language_learning.db`)
- **Prod**: PostgreSQL (update `DATABASES` in `app/config/settings.py`)

## 📦 Dependencies

- Django 4.2+, DRF, djangorestframework-simplejwt, drf-yasg, django-cors-headers

## 🔧 Configuration

`app/config/settings.py` — `DEBUG`, `SECRET_KEY`, `DATABASES`, `CORS_ALLOW_ALL_ORIGINS`

## 🛠️ Management Commands

| Command | Description |
|---------|-------------|
| `python manage.py create_test_admin` | Create/reset test admin |
| `python manage.py load_mock_data` | Load users, topics, content |
| `python manage.py generate_mock_submissions [--leaderboard]` | Generate SRS progress (add `--leaderboard` for varied dates & set completions) |
| `python manage.py makemigrations` | Create migrations |
| `python manage.py migrate` | Apply migrations |
| `python manage.py runserver` | Start dev server |
| `python manage.py test` | Run tests |

## 📖 Documentation

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## 📝 Logging

Configurable via `app/core/logger.py` + Django settings:

```python
from app.core.logger import get_logger
logger = get_logger(__name__)
logger.info("Hello")
```

Settings: `LOG_LEVEL`, `LOG_FILE`, `LOG_CONSOLE_OUTPUT`, `LOG_FILE_OUTPUT`, `LOG_FORMAT`, `LOG_DATE_FORMAT`

## 📄 License

MIT

## 👨‍💻 Author

Language Learning App Team
