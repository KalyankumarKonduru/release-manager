# Project Structure Documentation

Complete file listing and descriptions for the DevOps Release Manager backend.

## Core Application Files

### `/app/__init__.py`
- Empty initialization file for Python package

### `/app/main.py` (194 lines)
**FastAPI Application Factory**

Key Components:
- `lifespan()` - Async context manager handling startup/shutdown
  - Initializes database and Redis connections
  - Creates database tables
  - Closes connections gracefully on shutdown
- `create_app()` - FastAPI application factory
  - Configures CORS middleware
  - Registers health check endpoint (`/health`)
  - Sets up exception handlers for ValueError, RuntimeError, Exception
  - Configures OpenAPI documentation
  - Placeholder for API router registration

**Exception Handlers:**
- `ValueError` → 400 Bad Request
- `RuntimeError` → 500 Internal Server Error
- Generic exceptions → 500 Internal Server Error

**Endpoints:**
- `GET /` - Root endpoint with API metadata
- `GET /health` - Health check with dependency status
- `GET /api/v1/docs` - Swagger UI documentation
- `GET /api/v1/redoc` - ReDoc documentation

## Core Configuration Module (`/app/core/`)

### `/app/core/__init__.py`
- Empty initialization file

### `/app/core/config.py` (77 lines)
**Pydantic Settings Management**

Configuration Class: `Settings(BaseSettings)`

**Application Settings:**
- `APP_NAME` - Default: "DevOps Release Manager"
- `DEBUG` - Default: False
- `ENVIRONMENT` - Default: "development"

**API Configuration:**
- `API_V1_PREFIX` - Default: "/api/v1"
- `ALLOWED_HOSTS` - Default: ["*"]

**Database Settings:**
- `DATABASE_URL` - PostgreSQL connection (async with asyncpg)
- `DB_ECHO` - Log SQL statements
- `DB_POOL_SIZE` - Default: 20
- `DB_MAX_OVERFLOW` - Default: 0

**Redis Settings:**
- `REDIS_URL` - Redis connection
- `REDIS_TIMEOUT` - Default: 300 seconds

**Security Settings:**
- `SECRET_KEY` - JWT signing key
- `ALGORITHM` - Default: "HS256"
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Default: 30
- `REFRESH_TOKEN_EXPIRE_DAYS` - Default: 7

**CORS Settings:**
- `CORS_ORIGINS` - Default: localhost:3000, localhost:8000
- `CORS_ALLOW_CREDENTIALS` - Default: True
- `CORS_ALLOW_METHODS` - Default: ["*"]
- `CORS_ALLOW_HEADERS` - Default: ["*"]

**Optional GCP Settings:**
- `GCP_PROJECT_ID`
- `GCP_REGION`

**Logging:**
- `LOG_LEVEL` - Default: "INFO"

**Features:**
- Environment file support (.env)
- Type validation with Pydantic v2
- Property accessors for database/redis URLs

### `/app/core/database.py` (174 lines)
**SQLAlchemy 2.0 Async Database Management**

Classes:
- `Base` - Declarative base for ORM models
- `DatabaseManager` - Database lifecycle management

**DatabaseManager Methods:**
- `initialize()` - Creates async engine with asyncpg
  - Connection pooling configuration
  - Pool recycling (1 hour)
  - Socket timeouts
- `close()` - Disposes engine connections
- `create_tables()` - Creates all ORM model tables
- `drop_tables()` - Drops all tables (testing only)
- `get_session_factory()` - Returns sessionmaker
- `get_session()` - Async generator for session dependency

**Features:**
- AsyncSession from sqlalchemy.ext.asyncio
- Connection pool management
- Health check with pool_pre_ping
- Proper cleanup on shutdown

**Global Instance:**
- `db` - DatabaseManager singleton
- `get_db()` - FastAPI dependency for session injection

### `/app/core/security.py` (254 lines)
**JWT Token & Password Management**

Models:
- `TokenData` - Token payload structure
- `TokenResponse` - Token response with metadata

**Functions:**
- `hash_password(password)` - Bcrypt password hashing
- `verify_password(plain, hashed)` - Password verification
- `create_access_token(data, expires_delta)` - JWT access token creation
- `create_refresh_token(data)` - JWT refresh token creation
- `verify_token(token, token_type)` - Token validation and decoding
- `get_current_user(token)` - FastAPI dependency for current user
- `create_tokens(user_id)` - Create both token types

**Features:**
- JOSE JWT with HS256 algorithm
- Passlib bcrypt password hashing
- Token type validation
- Timezone-aware timestamps (UTC)
- Comprehensive error handling

**Constants:**
- `pwd_context` - CryptContext for password operations

### `/app/core/redis.py` (298 lines)
**Redis Connection & Caching Management**

Class: `RedisManager`

**Methods:**
- `initialize()` - Creates async Redis connection pool
  - Socket timeout: 5s
  - Encoding: UTF-8
  - Keepalive enabled
- `close()` - Closes Redis connection
- `get_cache(key, namespace)` - Retrieve cached value
  - JSON deserialization
  - Default: 300s TTL
  - Returns None on missing key
- `set_cache(key, value, ttl, namespace)` - Store value in cache
  - JSON serialization for complex types
  - Namespace-based key generation
  - Configurable TTL
- `delete_cache(key, namespace)` - Delete cache entry
- `invalidate_cache(pattern, namespace)` - Pattern-based deletion
  - Uses SCAN for large keysets
  - Wildcard pattern support
- `exists(key, namespace)` - Check key existence
- `increment(key, amount, namespace)` - Atomic increment
- `health_check()` - Redis connection health

**Features:**
- Namespaced cache keys (format: `namespace:key`)
- JSON serialization/deserialization
- Safe pattern matching with SCAN
- Error handling with fallback
- TTL support with default 300 seconds

**Global Instance:**
- `redis_manager` - RedisManager singleton
- `get_redis()` - FastAPI dependency for Redis client

## Additional Modules

### `/app/models/__init__.py`
Package for SQLAlchemy ORM models. Import all models here to register with Base.metadata.

### `/app/schemas/__init__.py`
Package for Pydantic request/response validation schemas.

### `/app/api/__init__.py`
Package for API route handlers and routers.

## Database Migration Files

### `/alembic/env.py` (96 lines)
**Alembic Async Migration Environment**

Features:
- Async migration support
- Target metadata configuration
- Offline and online migration modes
- Error handling and logging

### `/alembic/script.py.mako`
Alembic migration template for generated migration files.

### `/alembic/__init__.py`
Empty initialization file.

### `/alembic/versions/`
Directory for migration files (initially empty).

### `/alembic.ini`
Standard Alembic configuration file with logging setup.

## Configuration Files

### `/requirements.txt`
**Pinned Dependencies (Production-Ready)**

Core Framework:
- fastapi==0.109.0
- uvicorn[standard]==0.27.0

Database:
- sqlalchemy[asyncio]==2.0.25
- asyncpg==0.29.0
- alembic==1.13.1

Validation:
- pydantic==2.5.3
- pydantic-settings==2.1.0

Security:
- python-jose[cryptography]==3.3.0
- passlib[bcrypt]==1.7.4
- cryptography==41.0.7

Caching:
- redis==5.0.1

HTTP:
- httpx==0.26.0
- python-multipart==0.0.6
- python-dotenv==1.0.0

Testing:
- pytest==7.4.4
- pytest-asyncio==0.23.3
- pytest-cov==4.1.0

Code Quality (Optional):
- black==23.12.1
- flake8==6.1.0
- isort==5.13.2
- mypy==1.7.1

### `/pyproject.toml`
Project metadata and tool configurations:
- Build system configuration
- Project metadata
- Tool configurations (black, isort, mypy, pytest, coverage)

### `/.env.example`
Template environment variables file with defaults:
- Application config
- Database settings
- Redis settings
- Security settings
- CORS settings
- GCP settings (optional)

## Docker Files

### `/Dockerfile`
Multi-stage production image:
- Build stage: Installs dependencies
- Final stage: Minimal runtime image
  - Python 3.11-slim base
  - PostgreSQL client included
  - Health check endpoint
  - Exposed port 8000

### `/docker-compose.yml`
Complete local development environment:
- PostgreSQL 15 service
- Redis 7 service
- FastAPI service
- Health checks for all services
- Volume management
- Network isolation

### `/.dockerignore`
Excludes unnecessary files from Docker builds.

## Documentation Files

### `/README.md`
Comprehensive documentation including:
- Technology stack overview
- Project structure
- Installation and setup instructions
- Configuration options
- API endpoints
- Development workflow
- Docker deployment
- Troubleshooting guide

### `/QUICKSTART.md`
5-minute quick start guide:
- Local development setup
- Docker Compose setup
- Verification steps
- Development workflow
- Common tasks
- Environment variables
- Troubleshooting

### `/STRUCTURE.md`
This file - detailed file descriptions and organization.

## Development Files

### `/Makefile`
Development commands:
- install - Install dependencies
- dev - Run development server
- test - Run test suite
- test-cov - Run tests with coverage
- lint - Run code linting
- format - Format code
- migrate - Run migrations
- migrate-new - Create new migration
- clean - Clean temporary files
- docker-build - Build Docker image
- docker-run - Run Docker container

### `/conftest.py`
Pytest configuration and shared fixtures:
- Event loop fixture for async tests
- Test database setup (in-memory SQLite)
- FastAPI test app
- HTTP test client
- Test user data
- Test tokens

### `/.gitignore`
Git ignore patterns for:
- Environment files
- Python cache
- Virtual environments
- IDE files
- Test coverage
- Database files

## Summary

**Total Files Created: 26**

### By Category:
- **Core Application**: 8 files (app core modules)
- **Database & Migrations**: 5 files (alembic)
- **Configuration**: 4 files (requirements, pyproject, .env, alembic.ini)
- **Docker**: 3 files (Dockerfile, docker-compose, .dockerignore)
- **Development**: 3 files (Makefile, conftest, .gitignore)
- **Documentation**: 3 files (README, QUICKSTART, STRUCTURE)

### Code Statistics:
- **Production Code**: ~1,000 lines
- **Configuration**: ~300 lines
- **Documentation**: ~1,500 lines
- **Total**: ~2,800 lines

### Key Features:
- ✅ Async/await throughout
- ✅ Type hints on all functions
- ✅ Comprehensive docstrings
- ✅ Error handling
- ✅ Database connection pooling
- ✅ Redis caching with namespacing
- ✅ JWT authentication
- ✅ Password hashing
- ✅ CORS configuration
- ✅ Health checks
- ✅ Docker support
- ✅ Database migrations
- ✅ Testing setup
- ✅ Code quality tools configured
