# Backend Architecture

Visual guide to the DevOps Release Manager backend architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT APPLICATIONS                          │
│                    (Web UI, Mobile, CLI Tools)                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │ HTTP/HTTPS
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FASTAPI SERVER                             │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Lifespan Manager (Startup/Shutdown)                          │  │
│  │  - Initialize database connection pool                        │  │
│  │  - Initialize Redis connection pool                           │  │
│  │  - Create database tables                                     │  │
│  │  - Graceful shutdown                                          │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Middleware                                                     │  │
│  │  - CORS: Cross-Origin Resource Sharing                        │  │
│  │  - Error handlers (ValueError, RuntimeError, etc.)            │  │
│  │  - Logging and monitoring                                     │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ API Routers (v1)                                              │  │
│  │  - /api/v1/users/        (User management)                    │  │
│  │  - /api/v1/releases/     (Release management)                 │  │
│  │  - /api/v1/deployments/  (Deployment tracking)                │  │
│  │  - /api/v1/auth/         (Authentication)                     │  │
│  │  - /health               (Health check)                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ Request Processing Pipeline                                   │  │
│  │  1. Request → Schema Validation (Pydantic)                    │  │
│  │  2. Dependency Injection (FastAPI)                            │  │
│  │  3. Business Logic                                            │  │
│  │  4. Database/Cache Operations                                 │  │
│  │  5. Response → Schema Serialization                           │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
        ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
        │  PostgreSQL  │  │    Redis     │  │   Logging    │
        │  Database    │  │    Cache     │  │   System     │
        │  (Async)     │  │   (Async)    │  │              │
        └──────────────┘  └──────────────┘  └──────────────┘
```

## Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Presentation Layer (API Routers)                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ app/api/v1/users.py                                    │ │
│ │ app/api/v1/releases.py                                 │ │
│ │ Handles HTTP requests, returns JSON responses          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Validation Layer (Pydantic Schemas)                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ app/schemas/user.py                                    │ │
│ │ app/schemas/release.py                                 │ │
│ │ Request validation, response serialization             │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Business Logic Layer                                        │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Service functions, authentication, authorization       │ │
│ │ from app.core.security import verify_password          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Data Access Layer (Models + ORM)                            │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ app/models/user.py (SQLAlchemy models)                 │ │
│ │ Database queries, transactions                          │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                            ▼
┌─────────────────────────────────────────────────────────────┐
│ Persistence Layer                                           │
│ ┌──────────────────────┐      ┌──────────────────────────┐ │
│ │ PostgreSQL Database  │      │ Redis Cache              │ │
│ │ - Tables            │      │ - Sessions              │ │
│ │ - Indexes           │      │ - Cached queries        │ │
│ │ - Constraints       │      │ - Rate limiting         │ │
│ └──────────────────────┘      └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Component Interaction

```
Request Flow:
─────────────

1. HTTP Request arrives
        │
        ▼
2. FastAPI router matches endpoint
        │
        ▼
3. Pydantic schema validates request body
        │
        ▼
4. Dependency injection injects dependencies:
   - get_db: AsyncSession
   - get_redis: Redis client
   - get_current_user: User from token
        │
        ▼
5. Business logic executes:
   - Check cache first (Redis)
   - Query database if needed (PostgreSQL)
   - Perform transformations
   - Update cache
        │
        ▼
6. Response schema serializes data
        │
        ▼
7. HTTP Response returned to client


Cache Strategy:
───────────────

Request → Check Redis (Namespaced Key)
           ├─ Cache Hit: Return cached data
           └─ Cache Miss:
              │
              ▼
              Query Database
              │
              ▼
              Store in Redis (with TTL)
              │
              ▼
              Return data


Authentication Flow:
────────────────────

1. Client sends credentials (username + password)
        │
        ▼
2. Server verifies password (bcrypt)
        │
        ▼
3. Server creates JWT tokens:
   - Access token (short-lived, 30 min)
   - Refresh token (long-lived, 7 days)
        │
        ▼
4. Client stores tokens
        │
        ▼
5. Client includes access token in Authorization header
        │
        ▼
6. Server verifies token signature
        │
        ▼
7. Extract user ID from token claims
        │
        ▼
8. Continue processing request as authenticated user
```

## Core Modules Dependency Graph

```
┌────────────────────────────────────────────────────────────┐
│ app/main.py (FastAPI Application)                         │
│ - Imports: config, database, redis, security              │
│ - Uses: Lifespan, CORS, Exception handlers                │
│ - Provides: app instance                                  │
└────────────────────────────────────────────────────────────┘
         │      │      │      │
         ▼      ▼      ▼      ▼
    ┌────────┬────────┬────────┬────────┐
    │        │        │        │        │
    ▼        ▼        ▼        ▼        ▼
config  database redis  security routers
module  module   module  module  module
    │        │        │        │
    │        │        │        └──────────────┐
    │        │        │                       │
    │        └────────┼───────────────────────┤
    │                 │                       │
    │        ┌────────┘                       │
    │        ▼                                │
app/core/config.py                     app/api/v1/*
- Settings class                       - Router functions
- Environment variables                - Dependency injection
- Configuration management             - Request validation
- DB/Redis URLs                        - Response serialization

app/core/database.py
- DatabaseManager class
- AsyncEngine creation
- SessionFactory
- get_db dependency

app/core/redis.py
- RedisManager class
- Connection pooling
- Cache operations (get/set/delete)
- get_redis dependency

app/core/security.py
- Password hashing (bcrypt)
- JWT token creation/verification
- get_current_user dependency
- TokenData model
```

## Database Schema Organization

```
PostgreSQL Database: release_manager
├── users table
│   ├── id (PRIMARY KEY)
│   ├── email (UNIQUE)
│   ├── username (UNIQUE)
│   ├── password_hash
│   ├── created_at
│   └── updated_at
│
├── releases table
│   ├── id (PRIMARY KEY)
│   ├── name
│   ├── version
│   ├── status
│   ├── created_by (FOREIGN KEY → users)
│   ├── created_at
│   └── updated_at
│
├── deployments table
│   ├── id (PRIMARY KEY)
│   ├── release_id (FOREIGN KEY → releases)
│   ├── environment
│   ├── status
│   ├── deployed_at
│   └── deployed_by (FOREIGN KEY → users)
│
└── [More tables as needed]


Indexes:
├── users.email
├── users.username
├── releases.status
├── deployments.environment
└── deployments.deployed_at
```

## Redis Cache Structure

```
Redis (Key-Value Store): redis://localhost:6379/0

Namespaced Keys:
├── api:users:{user_id}
│   └── JSON: UserResponse
│
├── api:users:list:{skip}:{limit}
│   └── JSON: UserListResponse
│
├── api:releases:all
│   └── JSON: [ReleaseResponse]
│
├── auth:refresh:{user_id}
│   └── String: refresh_token
│
├── cache:releases:{release_id}
│   └── JSON: ReleaseDetailResponse
│
└── session:{session_id}
    └── JSON: SessionData


TTL (Time-To-Live):
├── Default: 300 seconds (5 minutes)
├── User data: 600 seconds (10 minutes)
├── Release data: 1800 seconds (30 minutes)
└── Auth tokens: 86400 seconds (24 hours)
```

## Deployment Architecture

```
Local Development:
─────────────────
┌──────────────────────┐
│ Docker Host Machine  │
│  (Your Computer)     │
│                      │
│ ┌────────────────┐  │
│ │ FastAPI        │  │
│ │ Container      │  │
│ │ :8000          │  │
│ └────────────────┘  │
│ ┌────────────────┐  │
│ │ PostgreSQL     │  │
│ │ Container      │  │
│ │ :5432          │  │
│ └────────────────┘  │
│ ┌────────────────┐  │
│ │ Redis          │  │
│ │ Container      │  │
│ │ :6379          │  │
│ └────────────────┘  │
└──────────────────────┘
      (docker-compose)


Production Deployment:
─────────────────────
┌────────────────────────────────────┐
│      Kubernetes Cluster            │
│                                    │
│  ┌──────────┐  ┌──────────┐       │
│  │ Release  │  │ Release  │       │
│  │ Manager  │  │ Manager  │       │
│  │ Pod 1    │  │ Pod 2    │  ... │
│  │ :8000    │  │ :8000    │       │
│  └──────────┘  └──────────┘       │
│        │             │             │
│        └─────┬───────┘             │
│              ▼                     │
│        ┌──────────────┐           │
│        │ Service      │           │
│        │ Load Balancer│           │
│        └──────────────┘           │
└────────────────────────────────────┘
              │
    ┌─────────┴──────────┐
    ▼                    ▼
┌──────────┐        ┌──────────┐
│PostgreSQL│        │  Redis   │
│Cluster   │        │Cluster   │
│(RDS/    │        │(ElastiC- │
│ PostgreSQL        │ache)     │
└──────────┘        └──────────┘
```

## Error Handling Flow

```
HTTP Request
     │
     ▼
Try: Process request
     │
     ├─ Pydantic validation fails
     │  └─→ Raise ValidationError
     │      └─→ Exception handler
     │          └─→ 422 Unprocessable Entity
     │
     ├─ Business logic fails
     │  └─→ Raise ValueError
     │      └─→ Exception handler
     │          └─→ 400 Bad Request
     │
     ├─ Database error
     │  └─→ Raise RuntimeError
     │      └─→ Exception handler
     │          └─→ 500 Internal Server Error
     │
     ├─ Not found
     │  └─→ Raise HTTPException(404)
     │      └─→ 404 Not Found
     │
     └─ Success
        └─→ Return response
            └─→ 200 OK (or appropriate status code)
```

## Data Flow Example: Create User

```
1. Client sends POST /api/v1/users/ with JSON body
        │
        ▼
2. FastAPI receives request
        │
        ▼
3. Pydantic validates against UserCreate schema
        │
        ▼
4. Dependency injection provides:
   - db: AsyncSession
   - Current request context
        │
        ▼
5. Route handler executes:
   a. Check cache for similar users (Redis)
   b. Hash password using bcrypt
   c. Create User model instance
   d. Execute INSERT into PostgreSQL
   e. Commit transaction
   f. Refresh model to get generated ID
   g. Invalidate relevant cache patterns
        │
        ▼
6. Response model serializes User to UserResponse
        │
        ▼
7. FastAPI returns JSON response with 201 status
        │
        ▼
8. Client receives response with created user data
```

## Key Design Patterns

### Dependency Injection
```
Router function defines dependencies:
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),  # Injected
    current_user: User = Depends(get_current_user)  # Injected
):
    pass
```

### Repository Pattern
```
Data access logic in models:
- SQLAlchemy ORM handles CRUD
- Service layer uses models
- Router functions use services
```

### Caching Strategy
```
Layered caching:
1. Request arrives
2. Check Redis cache
3. If miss, query database
4. Cache result
5. Return data
```

### Async-First Design
```
All I/O operations are async:
- Database queries
- Redis operations
- HTTP requests
- File operations
```

## Monitoring & Observability

```
Logging:
├── App level: app/main.py
├── Module level: Each module
├── SQL queries: DB_ECHO setting
└── Redis operations: redis_manager logs

Health Checks:
├── /health endpoint
├── Database connectivity
├── Redis connectivity
└── Application status

Metrics (Future):
├── Request duration
├── Cache hit rate
├── Error rate
└── Database query time
```

## Security Architecture

```
Authentication:
└── JWT Tokens
    ├── Access token: Short-lived (30 min)
    ├── Refresh token: Long-lived (7 days)
    └── HMAC-SHA256 signature

Password Storage:
└── Bcrypt hashing
    ├── Cost factor: 12 (configurable)
    └── Salt: Auto-generated

Authorization:
├── Role-based (future)
├── Resource ownership checks
└── Dependency injection for auth

CORS:
├── Configurable origins
├── Allowed methods and headers
└── Credentials support
```

This architecture provides a scalable, maintainable foundation for the DevOps Release Manager backend.
