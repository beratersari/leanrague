# Language Learning App - Backend

A Django-based backend for a Language Learning Application with n-layered architecture.

## 🏗️ Architecture

This project follows **n-layered architecture** pattern for clean separation of concerns:

```
app/
├── api/                 # API Layer (Presentation)
│   ├── urls.py          # URL routing
│   ├── views/           # API endpoints
│   │   ├── user_views.py
│   │   ├── subscription_views.py
│   │   └── content_views.py      # Topic, Flashcard, MCQ views
│   └── serializers/     # Data serialization
│       ├── user_serializers.py
│       ├── subscription_serializers.py
│       └── content_serializers.py  # Topic, Flashcard, MCQ serializers
├── services/            # Business Logic Layer
│   ├── user_service.py
│   ├── subscription_service.py
│   ├── topic_service.py
│   ├── flashcard_service.py
│   └── mcq_service.py
├── repositories/        # Data Access Layer
│   ├── user_repository.py
│   ├── subscription_repository.py
│   ├── topic_repository.py
│   ├── flashcard_repository.py
│   └── mcq_repository.py
├── models/              # Data Layer
│   ├── models.py        # All models (User, Subscription, Topic, Flashcard, MCQ)
│   └── apps.py
├── core/                # Core (exceptions, base classes)
├── authentication/      # JWT Authentication (Bearer optional)
├── permissions/         # Role-based access control
└── config/              # Configuration
```

## 👥 User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Admin** | Full system access | Manage all users, subscriptions, content |
| **Content Creator** | Content management | Create and manage learning content |
| **User** | Regular user | Access learning materials, manage own profile |

## 📋 Features

- ✅ **Authentication**: JWT-based authentication with refresh tokens
- ✅ **User Management**: CRUD operations for users with role management
- ✅ **Subscriptions**: Premium subscription system with plans (Free, Basic, Premium, Enterprise)
- ✅ **Content Management**: Topics, Flashcards, and MCQs for language learning
- ✅ **Role-based Access Control**: Permission classes for each role
- ✅ **Swagger Documentation**: Interactive API documentation
- ✅ **SQLite3 Database**: Development database (easily migrate to PostgreSQL)

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd zed-base
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (Admin)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the server**
   ```bash
   python manage.py runserver
   ```

7. **Access Swagger Documentation**
   ```
   http://localhost:8000/swagger/
   ```

### 🧪 Test Admin User

A test admin user is pre-configured for development and testing:

| Field | Value |
|-------|-------|
| **Email** | `admin@languagelearning.com` |
| **Password** | `Admin123!@#` |
| **Role** | Admin |

**Create/Reset test admin:**
```bash
python manage.py create_test_admin
```

### 🎭 Load Mock Data

Load sample data for easy testing:

```bash
python manage.py load_mock_data
```

**Creates:**
- **1 Admin user**: `admin@test.com` / `Admin123!`
- **2 Content Creators**: `creator1@test.com`, `creator2@test.com` / `Creator123!`
- **5 Regular Users**: `user1@test.com` - `user5@test.com` / `User123!`
- **4 Subscriptions**: 2 Premium, 2 Basic, 6 Free

**Mock Users Summary:**
| Email | Password | Role | Subscription |
|-------|----------|------|--------------|
| `admin@test.com` | `Admin123!` | Admin | - |
| `creator1@test.com` | `Creator123!` | Content Creator | Basic |
| `creator2@test.com` | `Creator123!` | Content Creator | Free |
| `user1@test.com` | `User123!` | User | Premium (1yr) |
| `user2@test.com` | `User123!` | User | Premium (30d) |
| `user3@test.com` | `User123!` | User | Basic (90d) |
| `user4@test.com` | `User123!` | User | Free |
| `user5@test.com` | `User123!` | User | Free |

**Quick Test:**
```bash
# 1. Load mock data
python manage.py load_mock_data

# 2. Login as admin
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@test.com", "password": "Admin123!"}'

# 3. Access admin endpoints with the token
curl -X GET http://localhost:8000/api/users/ \
  -H "Authorization: Bearer <your_access_token>"
```

⚠️ **Security Note**: Change default passwords in production!

## 📚 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/register/` | Register new user | No |
| POST | `/api/auth/login/` | Login and get tokens | No |
| POST | `/api/auth/refresh/` | Refresh access token | No |

### User Profile

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET/PUT/PATCH | `/api/users/profile/` | Manage own profile | Yes |
| POST | `/api/users/change-password/` | Change password | Yes |

### User Management (Admin Only)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create new user |
| GET | `/api/users/<id>/` | Get user details |
| PUT | `/api/users/<id>/` | Update user |
| DELETE | `/api/users/<id>/` | Delete user |
| GET | `/api/users/stats/` | Get user statistics |

### Subscriptions

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/subscriptions/` | Get my subscription | Yes |
| POST | `/api/subscriptions/` | Upgrade subscription | Yes |
| POST | `/api/subscriptions/cancel/` | Cancel subscription | Yes |
| GET | `/api/subscriptions/check-premium/` | Check premium access | Yes |

### Admin - Subscriptions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/subscriptions/` | List all subscriptions |
| POST | `/api/admin/subscriptions/` | Create subscription |
| GET | `/api/admin/subscriptions/<id>/` | Get subscription details |
| GET | `/api/admin/subscriptions/stats/` | Get subscription statistics |
| GET | `/api/admin/subscriptions/premium-users/` | List premium users |

### Content - Topics

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/content/topics/` | List all topics | Yes |
| POST | `/api/content/topics/` | Create topic (Admin/Creator) | Yes |
| GET | `/api/content/topics/<id>/` | Get topic details | Yes |
| PUT/PATCH | `/api/content/topics/<id>/` | Update topic | Yes |
| DELETE | `/api/content/topics/<id>/` | Delete topic | Yes |

### Content - Flashcard Sets

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/content/flashcard-sets/` | List all flashcard sets (filter by `?topic_id=`) | Yes |
| POST | `/api/content/flashcard-sets/` | Create flashcard set | Yes |
| GET | `/api/content/flashcard-sets/<id>/` | Get set with all flashcards | Yes |
| PUT/PATCH | `/api/content/flashcard-sets/<id>/` | Update set | Yes |
| DELETE | `/api/content/flashcard-sets/<id>/` | Delete set | Yes |

### Content - Flashcards

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/content/flashcards/` | List all flashcards (filter by `?set_id=`) | Yes |
| POST | `/api/content/flashcards/` | Create flashcard | Yes |
| GET | `/api/content/flashcards/<id>/` | Get flashcard details | Yes |
| PUT/PATCH | `/api/content/flashcards/<id>/` | Update flashcard | Yes |
| DELETE | `/api/content/flashcards/<id>/` | Delete flashcard | Yes |
| GET | `/api/content/flashcards/random/<set_id>/?count=10` | Get random flashcards for study | Yes |

### Content - MCQ Sets

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/content/mcq-sets/` | List all MCQ sets (filter by `?topic_id=`) | Yes |
| POST | `/api/content/mcq-sets/` | Create MCQ set | Yes |
| GET | `/api/content/mcq-sets/<id>/` | Get set with all MCQs | Yes |
| PUT/PATCH | `/api/content/mcq-sets/<id>/` | Update set | Yes |
| DELETE | `/api/content/mcq-sets/<id>/` | Delete set | Yes |

### Content - MCQs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/content/mcqs/` | List all MCQs (filter by `?set_id=`) | Yes |
| POST | `/api/content/mcqs/` | Create MCQ | Yes |
| GET | `/api/content/mcqs/<id>/` | Get MCQ details | Yes |
| PUT/PATCH | `/api/content/mcqs/<id>/` | Update MCQ | Yes |
| DELETE | `/api/content/mcqs/<id>/` | Delete MCQ | Yes |
| GET | `/api/content/mcqs/quiz/<set_id>/?count=10` | Get MCQs for quiz (no answers shown) | Yes |
| POST | `/api/content/mcqs/check-answer/` | Check answer: `{"mcq_id": 1, "user_answer": "A"}` | Yes |
| GET | `/api/content/mcqs/random/<set_id>/?count=10` | Get random MCQs for study | Yes |

## 🔐 Authentication

### Getting Access Token

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "yourpassword"}'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "user",
    "role_display": "User",
    "is_verified": false
  }
}
```

### Using the Token

```bash
curl -X GET http://localhost:8000/api/users/profile/ \
  -H "Authorization: Bearer <your_access_token>"
```

## 🗄️ Database

- **Development**: SQLite3 (`language_learning.db` in project root)
- **Production**: PostgreSQL (update `DATABASES` in `app/config/settings.py`)

Database file location: `/app/language_learning.db`

## 📦 Dependencies

- Django 4.2+
- Django REST Framework
- djangorestframework-simplejwt
- drf-yasg (Swagger)
- django-cors-headers

## 🔧 Configuration

Main settings file: `app/config/settings.py`

Key settings:
- `DEBUG`: Set to `False` in production
- `SECRET_KEY`: Change in production
- `DATABASES`: Update for PostgreSQL in production
- `CORS_ALLOW_ALL_ORIGINS`: Set to specific origins in production

## 📝 Development

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Django Admin

Access at: `http://localhost:8000/admin/`

## 📖 Documentation

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## 🚀 Future Improvements

- [ ] Migrate to PostgreSQL
- [ ] Add lessons under topics (Topic → Lesson → Content)
- [ ] Add progress tracking and learning statistics
- [ ] Add spaced repetition algorithm (SRS)
- [ ] Add notifications system
- [ ] Add payment integration
- [ ] Add email verification
- [ ] Add rate limiting
- [ ] Add audio/media file uploads
- [ ] Add leaderboards and gamification

## 📄 License

MIT License

## 👨‍💻 Author

Language Learning App Team
