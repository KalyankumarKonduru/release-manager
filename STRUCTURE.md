# DevOps Release Manager - Project Structure

## Overview
This is a comprehensive DevOps Release Manager API built with FastAPI and Pydantic v2, designed to manage releases, deployments, approvals, and analytics for microservices.

## Directory Structure

### Pydantic Schemas (`app/schemas/`)

All schemas use Pydantic v2 with `model_config = ConfigDict(from_attributes=True)` and UUIDs as `uuid.UUID` types.

#### Schema Files:
1. **common.py** - Common schemas
   - `PaginatedResponse[T]` - Generic paginated response container
   - `HealthResponse` - Health check response
   - `MessageResponse` - Generic message response
   - `ErrorResponse` - Error response

2. **user.py** - User management
   - `UserCreate` - Request to create user
   - `UserUpdate` - Request to update user
   - `UserResponse` - User data response
   - `UserLogin` - Login credentials
   - `Token` - Token response with access/refresh tokens
   - `TokenPayload` - JWT payload structure

3. **team.py** - Team management
   - `TeamCreate` - Request to create team
   - `TeamUpdate` - Request to update team
   - `TeamResponse` - Team data response

4. **service.py** - Service management
   - `ServiceCreate` - Request to create service
   - `ServiceUpdate` - Request to update service
   - `ServiceResponse` - Service data response

5. **environment.py** - Environment management
   - `EnvironmentCreate` - Request to create environment
   - `EnvironmentUpdate` - Request to update environment
   - `EnvironmentResponse` - Environment data response

6. **release.py** - Release management
   - `ReleaseCreate` - Request to create release
   - `ReleaseUpdate` - Request to update release
   - `ReleaseResponse` - Release data response
   - `ReleaseListResponse` - Paginated release list

7. **deployment.py** - Deployment management
   - `DeploymentCreate` - Request to create deployment
   - `DeploymentUpdate` - Request to update deployment
   - `DeploymentResponse` - Deployment data response
   - `PipelineStageDetail` - Pipeline stage details
   - `DeploymentWithStages` - Deployment with all stages

8. **approval.py** - Approval workflow
   - `ApprovalCreate` - Request to create approval
   - `ApprovalUpdate` - Request to approve/reject
   - `ApprovalResponse` - Approval data response

9. **audit_log.py** - Audit logging
   - `AuditLogResponse` - Audit log entry
   - `AuditLogFilter` - Filter parameters for audit logs

10. **rollback.py** - Rollback management
    - `RollbackCreate` - Request to initiate rollback
    - `RollbackResponse` - Rollback data response

11. **runbook.py** - Runbook management
    - `RunbookCreate` - Request to create runbook
    - `RunbookUpdate` - Request to update runbook
    - `RunbookResponse` - Runbook data response

12. **deployment_metric.py** - Deployment metrics
    - `DeploymentMetricResponse` - Individual metric
    - `MetricsSummary` - DORA metrics summary (MTTR, deployment frequency, change failure rate, lead time)

13. **pipeline_stage.py** - Pipeline stage management
    - `PipelineStageCreate` - Request to create stage
    - `PipelineStageUpdate` - Request to update stage
    - `PipelineStageResponse` - Pipeline stage data response

14. **__init__.py** - Schema exports

### API Routes (`app/api/routes/`)

All routes use:
- Dependency injection for DB sessions via `Depends(get_db)`
- Current user authentication via `Depends(get_current_user)`
- Proper HTTP status codes (201 for creation, 404 for not found, etc.)
- SQLAlchemy 2.0 async select() statements
- Try/except with appropriate error responses
- Comprehensive docstrings for OpenAPI documentation

#### Route Files:

1. **auth.py** (`/api/auth`)
   - `POST /register` - Register new user
   - `POST /login` - Login with email/password (returns access + refresh tokens)
   - `GET /me` - Get current user info
   - `POST /refresh` - Refresh access token using refresh token

2. **releases.py** (`/api/releases`)
   - `POST /` - Create release
   - `GET /` - List releases (filters: service_id, status, pagination)
   - `GET /{id}` - Get specific release
   - `PUT /{id}` - Update release
   - `DELETE /{id}` - Delete release
   - `POST /{id}/deploy` - Trigger deployment
   - `GET /{id}/history` - Get release history using CTE

3. **deployments.py** (`/api/deployments`)
   - `POST /` - Create deployment
   - `GET /` - List deployments (filters: release_id, environment_id, status)
   - `GET /{id}` - Get specific deployment
   - `PUT /{id}` - Update deployment
   - `DELETE /{id}` - Delete deployment
   - `POST /{id}/approve` - Approve deployment
   - `POST /{id}/rollback` - Rollback deployment
   - `GET /{id}/stages` - Get deployment with all stages
   - `GET /{id}/logs` - Get deployment logs

4. **services.py** (`/api/services`)
   - `POST /` - Create service
   - `GET /` - List services (filters: team_id, pagination)
   - `GET /{id}` - Get specific service
   - `PUT /{id}` - Update service
   - `DELETE /{id}` - Delete service
   - `GET /{id}/releases` - Get service releases
   - `GET /{id}/health` - Get service health status

5. **environments.py** (`/api/environments`)
   - `POST /` - Create environment
   - `GET /` - List environments (filters: env_type, pagination)
   - `GET /{id}` - Get specific environment
   - `PUT /{id}` - Update environment
   - `DELETE /{id}` - Delete environment
   - `GET /{id}/deployments` - Get environment deployments

6. **approvals.py** (`/api/approvals`)
   - `POST /` - Create approval request
   - `GET /` - List approvals (filters: status, deployment_id, pagination)
   - `GET /{id}` - Get specific approval
   - `PUT /{id}` - Update approval (approve/reject with notes)
   - `DELETE /{id}` - Delete approval

7. **audit_logs.py** (`/api/audit-logs`)
   - `GET /` - List audit logs with filters (date range, action, resource type, user)
   - `GET /{id}` - Get specific audit log
   - `GET /export/csv` - Export audit logs as CSV

8. **rollbacks.py** (`/api/rollbacks`)
   - `POST /` - Initiate rollback
   - `GET /` - List rollbacks (filters: deployment_id, status, pagination)
   - `GET /{id}` - Get specific rollback
   - `GET /{id}/status` - Get rollback status and progress

9. **runbooks.py** (`/api/runbooks`)
   - `POST /` - Create runbook
   - `GET /` - List runbooks (filters: service_id, environment_id, pagination)
   - `GET /{id}` - Get specific runbook
   - `PUT /{id}` - Update runbook
   - `DELETE /{id}` - Delete runbook
   - `GET /search/full-text` - Search runbooks (title + content)

10. **analytics.py** (`/api/analytics`)
    - `GET /metrics/summary` - Get DORA metrics summary (MTTR, deployment frequency, change failure rate, lead time)
    - `GET /metrics/trends` - Get deployment trends (daily counts using window functions)
    - `GET /metrics/by-service` - Get metrics grouped by service
    - `GET /metrics/by-environment` - Get metrics grouped by environment

11. **health.py** (`/api`)
    - `GET /health` - Health check (app + database + redis status)

### API Router Configuration

**app/api/__init__.py**
- Creates main `api_router` using FastAPI's APIRouter
- Includes all route modules
- Can be included in main FastAPI app with: `app.include_router(api_router)`

### SQLAlchemy Models (`app/models/`)

1. **base.py** - Base model with common fields
   - `BaseModel` - Abstract base with id, created_at, updated_at

2. **user.py** - User model
   - id, email, username, full_name, hashed_password, is_active, is_admin
   - created_at, updated_at

3. **team.py** - Team model
   - id, name, description, slack_channel, member_count
   - created_at, updated_at

4. **service.py** - Service model
   - id, name, description, repository_url, team_id, slack_channel, owner_id, is_active
   - created_at, updated_at

5. **environment.py** - Environment model
   - id, name, description, environment_type, config_path, is_active
   - created_at, updated_at

6. **release.py** - Release model
   - id, service_id, version, status, release_notes, git_commit, created_by
   - created_at, updated_at

7. **deployment.py** - Deployment model
   - id, release_id, environment_id, status, deployed_by, deployed_at, completed_at
   - created_at, updated_at
   - Relationship: stages (PipelineStage)

8. **approval.py** - Approval model
   - id, deployment_id, approver_id, status, notes, approved_at
   - created_at, updated_at

9. **audit_log.py** - Audit log model
   - id, user_id, action, resource_type, resource_id, details (JSON), ip_address, user_agent
   - created_at (no updated_at)

10. **rollback.py** - Rollback model
    - id, deployment_id, target_release_id, reason, status, initiated_by, completed_at
    - created_at, updated_at

11. **runbook.py** - Runbook model
    - id, title, content, service_id, environment_id, tags (JSON), created_by, is_active
    - created_at, updated_at

12. **deployment_metric.py** - Deployment metric model
    - id, deployment_id, metric_name, metric_value, unit
    - created_at, updated_at

13. **pipeline_stage.py** - Pipeline stage model
    - id, deployment_id, name, order, status, timeout_seconds, started_at, completed_at, output
    - created_at, updated_at
    - Relationship: deployment (Deployment)

### Core Utilities (`app/core/`)

1. **database.py**
   - `get_db()` - Database session dependency
   - SQLAlchemy async engine and session factory
   - Supports async operations with AsyncSession

2. **security.py**
   - `hash_password()` - Hash password with bcrypt
   - `verify_password()` - Verify password against hash
   - `create_token()` - Create JWT token
   - `decode_token()` - Decode and verify JWT token

## Key Features

### Authentication
- JWT-based authentication with access and refresh tokens
- Password hashing with bcrypt
- User registration and login endpoints
- Token expiration handling

### Release Management
- Full CRUD operations for releases
- Version tracking and git commit references
- Release history/chain using CTEs
- Status tracking (draft, published, deployed, failed)

### Deployment Management
- Deployment to multiple environments
- Approval workflow for deployments
- Rollback capability with target release selection
- Pipeline stages with timeout tracking
- Deployment logs integration

### Approval Workflow
- Create approval requests for deployments
- Approve or reject with notes
- Track approver and approval timestamps
- Filter by status and deployment

### Audit Logging
- Track all user actions (create, update, delete, deploy)
- Store IP address and user agent
- Filter by date range, action, resource type, user
- CSV export functionality

### Analytics & Metrics
- DORA metrics (Mean Time To Recovery, Deployment Frequency, Change Failure Rate, Lead Time)
- Deployment trends with window functions
- Per-service metrics
- Per-environment metrics
- Configurable analysis period

### Runbooks
- Create and manage operational runbooks
- Markdown content support
- Full-text search across title and content
- Tag-based organization
- Service and environment association

## Data Types

### UUIDs
All `id` fields use `UUID` type with default `uuid4()` generation

### DateTime Fields
All timestamp fields use `datetime` type with UTC timezone

### Pagination
- Default `skip=0`, `limit=50`
- Maximum `limit=500`
- Includes `total`, `page`, `page_size`, `total_pages`

### Query Filters
Most list endpoints support optional filters:
- Status filters (exact match)
- ID filters (exact match)
- Date range filters (start_date, end_date)
- Text search with LIKE patterns
- Pagination with skip/limit

## Error Handling

All endpoints include:
- 404 NOT_FOUND for missing resources
- 400 BAD_REQUEST for invalid input
- 401 UNAUTHORIZED for authentication failures
- 500 INTERNAL_SERVER_ERROR for server errors
- Detailed error messages in responses

## Database Setup

Models use SQLAlchemy 2.0 with:
- Type hints for all columns
- ForeignKey relationships
- Indexes on commonly filtered fields
- JSON columns for flexible data storage
- Default values and constraints

To create tables:
```python
from app.models.base import Base
from app.core.database import engine

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```
