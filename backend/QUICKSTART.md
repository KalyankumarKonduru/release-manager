# Quick Start Guide

Get the DevOps Release Manager backend up and running in 5 minutes.

## Option 1: Local Development (Fastest)

### Prerequisites
- Python 3.11+
- PostgreSQL 15
- Redis 5.0+

### Steps

```bash
# 1. Navigate to backend directory
cd /sessions/ecstatic-blissful-mayer/release-manager/backend

# 2. Create and activate virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment file
cp .env.example .env
# Edit .env and update DATABASE_URL and REDIS_URL if needed

# 5. Create database (PostgreSQL must be running)
createdb release_manager

# 6. Run migrations
alembic upgrade head

# 7. Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/v1/docs`
- Health Check: `http://localhost:8000/health`

## Option 2: Docker Compose (Recommended)

### Prerequisites
- Docker & Docker Compose

### Steps

```bash
# 1. Navigate to backend directory
cd /sessions/ecstatic-blissful-mayer/release-manager/backend

# 2. Create .env file (optional, uses defaults if not present)
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Check status
docker-compose ps

# 5. View logs
docker-compose logs -f api
```

Access the API at: `http://localhost:8000`

### Cleanup

```bash
# Stop all services
docker-compose down

# Remove volumes (careful!)
docker-compose down -v
```

## Verify Installation

### Health Check
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "DevOps Release Manager",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected"
}
```

### API Documentation
Open in browser:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

## Development Workflow

### Using Make Commands

```bash
# View all available commands
make help

# Install dependencies
make install

# Run development server
make dev

# Run tests
make test

# Format code
make format

# Run linting
make lint

# Create database migration
make migrate-new MSG="Add users table"

# Apply migrations
make migrate

# Clean temporary files
make clean
```

## Common Tasks

### Create a New API Endpoint

1. **Create schema** (`app/schemas/user.py`):
```python
from pydantic import BaseModel

class UserCreate(BaseModel):
    username: str
    email: str
```

2. **Create model** (`app/models/user.py`):
```python
from sqlalchemy import Column, Integer, String
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
```

3. **Create router** (`app/api/v1/users.py`):
```python
from fastapi import APIRouter
router = APIRouter(prefix="/users", tags=["users"])

@router.get("/")
async def list_users():
    return []
```

4. **Register router** in `app/main.py`:
```python
from app.api.v1 import users
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
```

5. **Create migration**:
```bash
make migrate-new MSG="Add users table"
make migrate
```

### Run Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_security.py -v

# Run with coverage
make test-cov

# View coverage report
open htmlcov/index.html
```

### Database Operations

```bash
# Show current migration version
alembic current

# Show migration history
alembic history

# Rollback one migration
alembic downgrade -1

# Rollback to base
alembic downgrade base

# Create new migration
alembic revision --autogenerate -m "Description"
```

## Environment Variables

Key environment variables in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/release_manager

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-change-in-production

# API
API_V1_PREFIX=/api/v1

# Development
DEBUG=true
ENVIRONMENT=development
LOG_LEVEL=INFO
```

## Troubleshooting

### Database Connection Error

```bash
# Test PostgreSQL connection
psql -h localhost -U user -d release_manager

# Check if PostgreSQL is running
pg_isready -h localhost

# Reset database
dropdb release_manager
createdb release_manager
alembic upgrade head
```

### Redis Connection Error

```bash
# Test Redis connection
redis-cli ping

# Check if Redis is running
redis-cli --latency
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Docker Issues

```bash
# Rebuild image
docker-compose build --no-cache

# Reset everything
docker-compose down -v
docker-compose up -d

# View full logs
docker-compose logs
```

## Next Steps

1. **Read Full Documentation**: See `README.md` for comprehensive guide
2. **Define Models**: Create ORM models in `app/models/`
3. **Create Schemas**: Define request/response models in `app/schemas/`
4. **Build Routers**: Create API endpoints in `app/api/v1/`
5. **Add Tests**: Write tests in `tests/` directory
6. **Deploy**: Use Docker for production deployment

## Getting Help

- Check the comprehensive `README.md`
- Review code in `app/core/` for examples
- Run `make help` for available commands
- Check `pyproject.toml` for tool configurations
- Look at `docker-compose.yml` for service setup

## Key Directories

```
backend/
├── app/core/           # Configuration, database, security, redis
├── app/models/         # SQLAlchemy ORM models
├── app/schemas/        # Pydantic request/response models
├── app/api/            # API route handlers
├── alembic/            # Database migrations
├── tests/              # Test suite
└── docker-compose.yml  # Local development environment
```

## Default Credentials (Docker Compose)

**PostgreSQL:**
- User: `release_user`
- Password: `release_password`
- Database: `release_manager`

**Redis:**
- Password: `redis_password`

Change these in `.env` for production!
