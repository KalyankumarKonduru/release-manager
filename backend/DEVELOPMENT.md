# Development Guide

Complete guide for developing the DevOps Release Manager backend.

## Architecture Overview

The backend follows a layered architecture:

```
HTTP Requests
    ↓
API Routers (app/api/v1/)
    ↓
Schemas (Pydantic validation)
    ↓
Business Logic
    ↓
Models (SQLAlchemy ORM)
    ↓
Database / Cache
```

## Creating New Features

### Step 1: Define the Model

Create your ORM model in `app/models/your_feature.py`:

```python
"""Users model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base


class User(Base):
    """User database model."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email})>"
```

Then import it in `app/models/__init__.py`:

```python
from app.models.user import User

__all__ = ["User"]
```

### Step 2: Create Request/Response Schemas

Create schemas in `app/schemas/your_feature.py`:

```python
"""User schemas."""
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """User update schema."""

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    """User response schema."""

    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy support


class UserListResponse(BaseModel):
    """User list response."""

    total: int
    items: list[UserResponse]
```

Import in `app/schemas/__init__.py`:

```python
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse

__all__ = ["UserCreate", "UserUpdate", "UserResponse", "UserListResponse"]
```

### Step 3: Create API Router

Create router in `app/api/v1/users.py`:

```python
"""User API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.redis import redis_manager
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new user.

    Args:
        user_data: User creation data
        db: Database session

    Returns:
        Created user

    Raises:
        HTTPException: 400 if user already exists
    """
    # Check if user exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )

    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Invalidate cache
    await redis_manager.invalidate_cache("users:*")

    return user


@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
):
    """
    List all users with pagination.

    Args:
        skip: Number of users to skip
        limit: Maximum users to return
        db: Database session

    Returns:
        List of users
    """
    # Try cache first
    cache_key = f"users:list:{skip}:{limit}"
    cached = await redis_manager.get_cache(cache_key, namespace="api")
    if cached:
        return cached

    # Query database
    stmt = select(User).offset(skip).limit(limit)
    result = await db.execute(stmt)
    users = result.scalars().all()

    # Count total
    count_stmt = select(func.count(User.id))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar()

    response = UserListResponse(total=total, items=users)

    # Cache result
    await redis_manager.set_cache(cache_key, response.model_dump(), namespace="api")

    return response


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get a user by ID.

    Args:
        user_id: User ID
        db: Database session

    Returns:
        User data

    Raises:
        HTTPException: 404 if user not found
    """
    # Try cache
    cache_key = f"users:{user_id}"
    cached = await redis_manager.get_cache(cache_key, namespace="api")
    if cached:
        return cached

    # Query database
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Cache result
    await redis_manager.set_cache(cache_key, user, namespace="api")

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
):
    """
    Update a user.

    Args:
        user_id: User ID
        user_data: Updated user data
        db: Database session

    Returns:
        Updated user

    Raises:
        HTTPException: 404 if user not found
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update fields
    if user_data.email:
        user.email = user_data.email
    if user_data.username:
        user.username = user_data.username
    if user_data.full_name:
        user.full_name = user_data.full_name
    if user_data.password:
        user.password_hash = hash_password(user_data.password)

    await db.commit()
    await db.refresh(user)

    # Invalidate cache
    await redis_manager.delete_cache(f"users:{user_id}", namespace="api")
    await redis_manager.invalidate_cache("users:*")

    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a user.

    Args:
        user_id: User ID
        db: Database session

    Raises:
        HTTPException: 404 if user not found
    """
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await db.delete(user)
    await db.commit()

    # Invalidate cache
    await redis_manager.delete_cache(f"users:{user_id}", namespace="api")
    await redis_manager.invalidate_cache("users:*")
```

Register in `app/api/v1/__init__.py` or create a routers file.

### Step 4: Register Router in Main App

Update `app/main.py`:

```python
from app.api.v1 import users

# In create_app() function, add:
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
```

### Step 5: Create Database Migration

```bash
# Generate migration
alembic revision --autogenerate -m "Add users table"

# Apply migration
alembic upgrade head
```

### Step 6: Add Tests

Create `tests/test_users.py`:

```python
"""User endpoint tests."""
import pytest
from httpx import AsyncClient
from app.models.user import User
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_create_user(client: AsyncClient):
    """Test user creation."""
    response = await client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "TestPassword123",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_list_users(client: AsyncClient):
    """Test listing users."""
    response = await client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "items" in data
```

Run tests:

```bash
pytest tests/test_users.py -v
```

## Code Standards

### Type Hints

Always use type hints:

```python
# Bad
def get_user(user_id):
    return db.query(User).get(user_id)

# Good
async def get_user(user_id: int, db: AsyncSession) -> Optional[User]:
    """Get user by ID."""
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
```

### Docstrings

All functions should have docstrings:

```python
async def create_release(
    release_data: ReleaseCreate,
    db: AsyncSession = Depends(get_db),
) -> ReleaseResponse:
    """
    Create a new release.

    Args:
        release_data: Release creation data
        db: Database session

    Returns:
        Created release

    Raises:
        HTTPException: 400 if data is invalid
        HTTPException: 409 if release name already exists
    """
```

### Error Handling

Use appropriate HTTP status codes:

```python
from fastapi import HTTPException, status

# Bad request
raise HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="Invalid input",
)

# Not found
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail="Resource not found",
)

# Conflict
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Resource already exists",
)

# Unauthorized
raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Authentication required",
)
```

### Async/Await

All I/O operations must be async:

```python
# Bad - blocking operations
from time import sleep
def slow_operation():
    sleep(5)  # This blocks everything

# Good - async operations
import asyncio
async def async_operation():
    await asyncio.sleep(5)  # This doesn't block
    db = await get_db()  # Async database call
    result = await db.execute(stmt)
```

## Testing Best Practices

### Unit Tests

Test individual functions:

```python
@pytest.mark.asyncio
async def test_hash_password():
    """Test password hashing."""
    from app.core.security import hash_password, verify_password

    password = "TestPassword123"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("WrongPassword", hashed)
```

### Integration Tests

Test API endpoints:

```python
@pytest.mark.asyncio
async def test_user_workflow(client: AsyncClient):
    """Test complete user workflow."""
    # Create user
    create_response = await client.post("/api/v1/users/", json={...})
    assert create_response.status_code == 201
    user_id = create_response.json()["id"]

    # Get user
    get_response = await client.get(f"/api/v1/users/{user_id}")
    assert get_response.status_code == 200

    # Update user
    update_response = await client.put(
        f"/api/v1/users/{user_id}",
        json={"full_name": "Updated Name"}
    )
    assert update_response.status_code == 200

    # Delete user
    delete_response = await client.delete(f"/api/v1/users/{user_id}")
    assert delete_response.status_code == 204
```

### Run Tests

```bash
# All tests
pytest

# Specific file
pytest tests/test_users.py

# Specific test
pytest tests/test_users.py::test_create_user

# With output
pytest -v

# With coverage
pytest --cov=app

# Stop on first failure
pytest -x
```

## Database Migrations

### Create Migration

```bash
# Auto-generate (uses model changes)
alembic revision --autogenerate -m "Add users table"

# Manual migration
alembic revision -m "Custom migration"
```

### Review Migration

Check `alembic/versions/xxx_add_users_table.py` before applying:

```python
def upgrade() -> None:
    """Create users table."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        # ...
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username'),
    )


def downgrade() -> None:
    """Drop users table."""
    op.drop_table('users')
```

### Apply Migrations

```bash
# Forward
alembic upgrade head

# Backward (careful!)
alembic downgrade -1

# To specific version
alembic upgrade abc123def456

# Check current
alembic current

# Show history
alembic history
```

## Code Quality

### Format Code

```bash
# Black formatting
black .

# Import sorting
isort .

# Run both
make format
```

### Lint Code

```bash
# Flake8
flake8 app

# MyPy type checking
mypy app

# Run all
make lint
```

### Pre-commit Hooks

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
```

Install:

```bash
pip install pre-commit
pre-commit install
```

## Performance Optimization

### Query Optimization

```python
# Bad - N+1 query problem
users = db.query(User).all()
for user in users:
    print(user.releases)  # Query for each user!

# Good - eager loading
from sqlalchemy.orm import joinedload
stmt = select(User).options(joinedload(User.releases))
result = await db.execute(stmt)
users = result.unique().scalars().all()
```

### Caching

```python
# Cache database query results
cache_key = f"releases:all"
cached = await redis_manager.get_cache(cache_key)
if cached:
    return cached

# Query database
stmt = select(Release).limit(100)
result = await db.execute(stmt)
releases = result.scalars().all()

# Cache for 1 hour
await redis_manager.set_cache(cache_key, releases, ttl=3600)

return releases
```

### Pagination

```python
@router.get("/releases")
async def list_releases(
    skip: int = 0,
    limit: int = 10,
):
    """List releases with pagination."""
    stmt = select(Release).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return result.scalars().all()
```

## Debugging

### Enable SQL Logging

```python
# In .env
DB_ECHO=true
```

### Print Statements

```python
import logging
logger = logging.getLogger(__name__)

@router.get("/test")
async def test():
    logger.info("Starting operation")
    logger.debug("Debug info")
    logger.warning("Warning message")
    logger.error("Error message")
    return {"status": "ok"}
```

### Interactive Debugging

```python
import pdb; pdb.set_trace()

# In modern Python 3.7+
breakpoint()
```

## Common Patterns

### Dependency Injection

```python
async def get_current_user(
    token: str = Header(...),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current user from token."""
    user_id = verify_token(token)
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()

@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Get current user info."""
    return current_user
```

### Pagination

```python
class PaginationParams(BaseModel):
    skip: int = 0
    limit: int = 10

@router.get("/items")
async def list_items(
    params: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """List items with pagination."""
    stmt = select(Item).offset(params.skip).limit(params.limit)
    result = await db.execute(stmt)
    return result.scalars().all()
```

### Bulk Operations

```python
@router.post("/users/bulk")
async def bulk_create_users(
    users_data: list[UserCreate],
    db: AsyncSession = Depends(get_db),
):
    """Create multiple users."""
    users = [User(**data.model_dump()) for data in users_data]
    db.add_all(users)
    await db.commit()
    return users
```

## Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` in `.env`
- [ ] Set `DEBUG=false`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use strong database password
- [ ] Enable HTTPS
- [ ] Set up error monitoring
- [ ] Configure logging
- [ ] Set up backup strategy
- [ ] Run security audit
- [ ] Performance testing

### Docker Deployment

```bash
# Build
docker build -t release-manager:v1.0 .

# Run
docker run -d \
  --name release-manager \
  -p 8000:8000 \
  --env-file .env.production \
  release-manager:v1.0
```

### Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: release-manager-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: release-manager-api
  template:
    metadata:
      labels:
        app: release-manager-api
    spec:
      containers:
      - name: api
        image: release-manager:v1.0
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
```

## Useful Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [Redis Documentation](https://redis.io/docs/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)

## Getting Help

- Check project documentation (README, QUICKSTART, STRUCTURE)
- Review existing code for patterns
- Check FastAPI tutorials and examples
- Ask questions in code comments
- Run tests to understand behavior
