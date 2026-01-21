# NoteTaker Backend API

A Django REST API for the NoteTaker application - a simple, powerful note-taking platform with category management and user authentication.

## Overview

This backend service handles all the core functionality for NoteTaker: user authentication, note CRUD operations, and category management. Built with Django REST Framework, it provides a robust, scalable API that powers the frontend application.

## Tech Stack

- **Django 4.2** - Web framework
- **Django REST Framework** - API toolkit
- **PostgreSQL** - Database
- **JWT Authentication** - djangorestframework-simplejwt
- **CORS Headers** - django-cors-headers
- **Gunicorn** - Production WSGI server

## Features

### Authentication

- User registration with email validation
- JWT-based authentication (access & refresh tokens)
- Token refresh mechanism
- Secure logout with token blacklisting

### Notes Management

- Create, read, update, delete notes
- Rich text content support
- Automatic timestamp tracking
- Filter notes by category
- User-specific note isolation

### Categories

- Custom category creation
- Color-coded categories
- Note count tracking per category
- Category-based filtering

## Project Structure

```
Backend/
├── accounts/           # User authentication & management
│   ├── models.py      # Custom User model
│   ├── serializers.py # API serializers
│   ├── views.py       # API endpoints
│   └── urls.py        # Route definitions
├── notes/             # Notes & categories
│   ├── models.py      # Note & Category models
│   ├── serializers.py # API serializers
│   ├── views.py       # API endpoints
│   ├── signals.py     # Auto-update category counts
│   └── urls.py        # Route definitions
├── notetaker/         # Project settings
│   ├── settings.py    # Configuration
│   ├── urls.py        # Main URL routing
│   └── wsgi.py        # WSGI config
├── manage.py          # Django CLI
└── requirements.txt   # Python dependencies
```

## API Endpoints

### Authentication

```
POST   /api/auth/register/     - Register new user
POST   /api/auth/login/        - Login user
POST   /api/auth/logout/       - Logout user
GET    /api/auth/user/         - Get current user
POST   /api/auth/token/refresh/ - Refresh access token
```

### Categories

```
GET    /api/categories/        - List all categories
POST   /api/categories/        - Create category
PATCH  /api/categories/:id/    - Update category
DELETE /api/categories/:id/    - Delete category
```

### Notes

```
GET    /api/notes/             - List all notes (with optional category filter)
GET    /api/notes/:id/         - Get specific note
POST   /api/notes/             - Create note
PATCH  /api/notes/:id/         - Update note
DELETE /api/notes/:id/         - Delete note
```

## Setup & Installation

### Local Development

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Backend
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

4. **Set up PostgreSQL database**
   - Install PostgreSQL
   - Create database: `createdb notetaker`
   - Update credentials in `.env`

5. **Configure environment variables**

   ```bash
   # Create .env file with:
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DB_NAME=notetaker
   DB_USER=postgres
   DB_PASSWORD=your-password
   DB_HOST=localhost
   DB_PORT=5432
   ```

6. **Run migrations**

   ```bash
   python manage.py migrate
   ```

7. **Create superuser** (optional)

   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**

   ```bash
   python manage.py runserver
   ```

   API will be available at `http://localhost:8000/api/`

### Production Deployment

The app is configured for deployment on Railway, but works with any platform supporting Django.

1. **Set environment variables** on your hosting platform:
   - `SECRET_KEY` - Django secret key (generate a new one!)
   - `DEBUG` - Set to `False`
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` - Database credentials
   - Or use `DATABASE_URL` if your host provides it

2. **Run migrations** after deployment:

   ```bash
   python manage.py migrate
   ```

3. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

## Key Design Decisions

### 1. Custom User Model

I went with a custom User model from the start (extending `AbstractUser`) even though we're just using email. This gives us flexibility to add user fields later without painful migrations. It's one of those "do it now or regret it later" Django decisions.

### 2. JWT Over Session Authentication

Chose JWT tokens because:

- The frontend is completely separate (different domain)
- Easier to scale horizontally
- Simpler for mobile apps if we build one later
- No need to manage session storage

The trade-off is that tokens can't be invalidated server-side (except refresh tokens), but with short-lived access tokens (1 day) and refresh token rotation, we get good security.

### 3. Signals for Category Counts

Used Django signals to automatically update the `notes_count` on categories when notes are created/deleted. Alternative was to calculate it on-the-fly in serializers, but that would mean N+1 queries. This approach trades a bit of write complexity for much faster reads.

### 4. Separate Apps for Accounts & Notes

Could have put everything in one app, but separating concerns makes the codebase easier to understand and maintain. Each app has a clear responsibility, and you can look at one without being distracted by the other.

### 5. CORS Configuration

Set to allow all origins for easier deployment. In a more security-critical app, I'd lock this down to specific domains. For a note-taking app, the authentication layer provides sufficient security.

### 6. No CSRF for API

Disabled CSRF middleware because we're using JWT tokens. CSRF protection is for cookie-based auth. With token auth, the client has to explicitly include the token in headers, which CSRF attacks can't do.

## Development Process

### Initial Setup

Started by scaffolding out the Django project structure and setting up the models. The data model is pretty straightforward - Users, Categories, and Notes with simple relationships.

### Authentication Layer

Built the authentication system first since everything depends on it. Used `djangorestframework-simplejwt` which saved a ton of time - it handles token generation, validation, and refresh out of the box. Just needed to customize the serializers to return the format the frontend expected.

### API Development

Developed the API endpoints using DRF's generic views. Most endpoints are just basic CRUD, so `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`, etc. did the heavy lifting. Only had to override `create()` in a few places to customize the response format.

### Testing Approach

Wrote tests for all the critical paths - user registration/login, note CRUD, category operations. Focused on integration tests rather than unit tests since most of the logic is in Django/DRF internals. The tests caught a few edge cases with permissions and filtering.

### Deployment Configuration

Set up the production config to work smoothly with Railway. Main considerations:

- Environment-based settings (DEBUG, SECRET_KEY, DB credentials)
- CORS configuration for the deployed frontend
- Gunicorn for production server
- Static file handling
- Database connection pooling

## AI Tools Used

### GitHub Copilot

Used Copilot throughout development for:

- **Boilerplate reduction**: Generating serializers, viewsets, and URL patterns. Once you write one serializer, Copilot can suggest the pattern for others.
- **Test writing**: It's really good at suggesting test cases once you establish the pattern.
- **Django patterns**: Autocompleting common Django patterns like `get_queryset()` overrides.

I didn't just accept every suggestion blindly - reviewed each one and modified as needed. Sometimes Copilot would suggest outdated patterns or unnecessary complexity.

### Development Workflow

1. Planned features and data models manually
2. Wrote model definitions with Copilot assistance
3. Let AI suggest serializers and views, then refined them
4. Manually tested each endpoint in Postman
5. Used AI to help write tests for coverage
6. Debugged deployment issues with AI assistance

The AI tools probably saved 30-40% of development time, mainly on boilerplate and troubleshooting. But the architecture, design decisions, and critical logic were all manual work - you can't outsource thinking to AI yet.

## Testing

Run tests with:

```bash
python manage.py test
```

Tests cover:

- User authentication flow
- Token generation and validation
- Note CRUD operations
- Category management
- Permissions and access control
- Signal behavior
