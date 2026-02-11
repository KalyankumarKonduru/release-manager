# DevOps Release Manager - Backend API

A production-ready FastAPI backend for managing DevOps releases with PostgreSQL, Redis caching, and JWT authentication.

## Technology Stack

- **Framework**: FastAPI 0.109.0
- **Python**: 3.11+
- **Database**: PostgreSQL 15 with SQLAlchemy 2.0 (async)
- **Cache**: Redis 5.0.1
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Database Migrations**: Alembic 1.13.1
- **Testing**: pytest with async support

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application factory
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Pydantic settings management
│   │   ├── database.py         # SQLAlchemy async engine & session
│   │   ├── security.py         # JWT & password handling
│   │   └── redis.py            # Redis connection & caching
│   ├── models/                 # SQLAlchemy ORM models (to be created)
│   ├── schemas/                # Pydantic request/response schemas (to be created)
│   └── api/                    # API routers (to be created)
├── alembic/
│   ├── env.py                  # Alembic async configuration
│   ├── script.py.mako          # Migration template
│   └── versions/               # Migration files
├── tests/                      # Test suite (to be created)
├── requirements.txt            # Python dependencies
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Project metadata & tool config
├── Dockerfile                  # Container image definition
├── .env.example                # Environment variables template
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## Prerequisites

- Python 3.11+
- PostgreSQL 15+
- Redis 5.0+
- pip and virtualenv

## Installation & Setup

### 1. Clone and Setup Environment

```bash
cd /sessions/ecstatic-blissful-mayer/release-manager/backend

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip setuptools wheel
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
nano .env
```

**Key environment variables:**

```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/release_manager
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=true
```

### 4. Database Setup

```bash
# Create PostgreSQL database
createdb release_manager

# Run Alembic migrations
alembic upgrade head
```

### 5. Run Development Server

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py entry point
python -m app.main
```

The API will be available at `http://localhost:8000`

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Core Features

### Configuration Management (`app/core/config.py`)

- Environment-based settings using Pydantic v2
- Support for multiple environments (dev, staging, production)
- Type-safe configuration with validation
- Optional GCP integration settings

### Database Management (`app/core/database.py`)

- AsyncIO-based SQLAlchemy 2.0 engine
- Connection pooling with asyncpg
- Session factory for async operations
- Table initialization and cleanup utilities

### Security (`app/core/security.py`)

- JWT token creation and verification
- Password hashing with bcrypt
- Token refresh mechanism
- Current user dependency injection

### Redis Caching (`app/core/redis.py`)

- Async Redis connection management
- Namespaced cache operations
- TTL support for cached values
- Pattern-based cache invalidation
- Health check utilities

### FastAPI Application (`app/main.py`)

- Lifespan context manager for startup/shutdown
- CORS middleware configuration
- Health check endpoint
- Exception handlers
- OpenAPI documentation setup

## Development

### Code Quality

Run code formatting and linting:

```bash
# Format code with black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 app

# Type checking with mypy
mypy app
```

### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_security.py -v

# Run with markers
pytest -m unit -v
```

### Database Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add users table"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Check current revision
alembic current

# Show migration history
alembic history
```

## Docker Deployment

### Build Image

```bash
docker build -t release-manager:latest .
```

### Run Container

```bash
docker run -d \
  --name release-manager \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://user:pass@db:5432/release_manager" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e SECRET_KEY="your-secret-key" \
  release-manager:latest
```

### Docker Compose (Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
      POSTGRES_DB: release_manager
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://user:password@db:5432/release_manager
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: your-secret-key
      ENVIRONMENT: production
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

Run with: `docker-compose up -d`

## API Endpoints

### Health Check

```
GET /health
GET /
```

### Authentication (To be implemented)

```
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
```

### User Management (To be implemented)

```
GET /api/v1/users
POST /api/v1/users
GET /api/v1/users/{user_id}
PUT /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}
```

## Configuration Options

### Database Settings

- `DATABASE_URL`: PostgreSQL connection string
- `DB_ECHO`: Log all SQL statements (development only)
- `DB_POOL_SIZE`: Connection pool size (default: 20)
- `DB_MAX_OVERFLOW`: Max overflow connections (default: 0)

### Security Settings

- `SECRET_KEY`: JWT signing key (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration (default: 7)

### Redis Settings

- `REDIS_URL`: Redis connection URL
- `REDIS_TIMEOUT`: Cache TTL in seconds (default: 300)

### CORS Settings

- `CORS_ORIGINS`: Allowed origins
- `CORS_ALLOW_CREDENTIALS`: Allow cookies
- `CORS_ALLOW_METHODS`: Allowed HTTP methods
- `CORS_ALLOW_HEADERS`: Allowed headers

## Error Handling

The application includes custom exception handlers for:

- `ValueError`: 400 Bad Request
- `RuntimeError`: 500 Internal Server Error
- General exceptions: 500 Internal Server Error

All errors are logged and returned with appropriate HTTP status codes.

## Logging

Logging is configured via the `LOG_LEVEL` environment variable. Supported levels:

- DEBUG: Detailed information for development
- INFO: General information (default)
- WARNING: Warning messages
- ERROR: Error messages only
- CRITICAL: Critical errors only

## Performance Considerations

1. **Database**: Connection pooling is enabled by default
2. **Caching**: Use Redis for frequently accessed data
3. **Async**: All I/O operations are async by default
4. **Connection Timeout**: Set to 10 seconds
5. **Pool Recycling**: Connections recycled after 1 hour

## Security Best Practices

1. Change `SECRET_KEY` in production
2. Use strong database passwords
3. Enable HTTPS in production
4. Set `DEBUG=false` in production
5. Validate all input data
6. Use environment variables for secrets
7. Implement rate limiting (to be added)
8. Add authentication middleware to protected routes

## Troubleshooting

### Database Connection Issues

```bash
# Test PostgreSQL connection
psql -h localhost -U user -d release_manager

# Check Alembic configuration
alembic current
```

### Redis Connection Issues

```bash
# Test Redis connection
redis-cli ping
```

### Migration Issues

```bash
# Check Alembic history
alembic history

# Show current version
alembic current

# Reset to initial state (careful!)
alembic downgrade base
```

## Contributing

1. Create a virtual environment
2. Install development dependencies: `pip install -r requirements.txt`
3. Follow code style with black and isort
4. Add tests for new features
5. Ensure all tests pass: `pytest`
6. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and questions, please open an issue on GitHub or contact the DevOps team.
