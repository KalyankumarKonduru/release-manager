# Release Manager

A comprehensive DevOps release management platform for automating deployments, tracking release history, managing database migrations, and coordinating team workflows across multiple environments.

## Project Overview

Release Manager is a production-grade application that provides centralized control over the entire deployment lifecycle. It enables teams to safely manage releases across development, staging, and production environments with built-in safeguards, automated rollback capabilities, and complete audit trails.

**Key Features:**
- Automated deployment orchestration to multiple environments
- Release approval workflows with team collaboration
- One-click rollback with automatic health verification
- Database migration management with Alembic integration
- Comprehensive audit logging of all deployment actions
- Real-time deployment status monitoring and alerting
- Release notes generation and publication
- Team-based permission management

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Release Manager                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────────┐        ┌──────────────────────────┐   │
│  │   Web Interface     │        │  REST API (FastAPI)      │   │
│  │  - Release Workflow │────────│  - Deployments          │   │
│  │  - Status Dashboard │        │  - Rollbacks            │   │
│  │  - Release History  │        │  - Monitoring           │   │
│  │  - Audit Logs       │        │  - Authentication       │   │
│  └─────────────────────┘        └──────────────────────────┘   │
│           │                                │                    │
│           └────────────────┬───────────────┘                    │
│                            │                                    │
│        ┌───────────────────┴──────────────────┐                │
│        │                                      │                │
│  ┌─────▼──────────┐                 ┌────────▼──────────┐     │
│  │  Core Services │                 │ Integration Layer  │     │
│  │                │                 │                    │     │
│  │ - Release Mgmt │                 │ - Kubernetes API   │     │
│  │ - Deployment   │                 │ - PostgreSQL       │     │
│  │ - Rollback     │                 │ - Redis Cache      │     │
│  │ - Notifications│                 │ - Message Queue    │     │
│  │ - Audit Trail  │                 │ - External APIs    │     │
│  └────────────────┘                 └────────────────────┘     │
│        │                                     │                  │
└────────┼─────────────────────────────────────┼──────────────────┘
         │                                     │
     ┌───┴─────────────────────────────────────┴────┐
     │                                              │
 ┌───▼────────┐  ┌──────────────┐  ┌──────────────┐│
 │ Kubernetes  │  │  PostgreSQL   │  │   Redis      ││
 │ (K8s API)   │  │   (Data)      │  │  (Cache)     ││
 └────────────┘  └──────────────┘  └──────────────┘│
                                                    │
     ┌──────────────────────────────────────────────┘
     │
 ┌───┴──────────────────────┐
 │  Environment Targets      │
 │                           │
 │ - Development             │
 │ - Staging                 │
 │ - Production              │
 └───────────────────────────┘
```

## Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 18, TypeScript, Vite | Web UI for release management |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy | REST API and business logic |
| **Database** | PostgreSQL 14, Alembic | Data persistence and migrations |
| **Cache** | Redis 7 | Session and data caching |
| **Orchestration** | Kubernetes 1.27, Helm | Container orchestration and deployment |
| **Monitoring** | Prometheus, Grafana, ELK Stack | Metrics and logging |
| **Message Queue** | RabbitMQ 3.12 | Asynchronous task processing |
| **Container** | Docker, Docker Compose | Containerization |
| **IaC** | Terraform, Helm Charts | Infrastructure as Code |

## Quick Start

Get the Release Manager running locally in 3 steps:

```bash
# Clone the repository
git clone https://github.com/company/release-manager.git
cd release-manager

# Start all services with Docker Compose
docker-compose up -d

# Access the application
# Web UI: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

**Default credentials for local development:**
- Username: `admin`
- Password: `admin123`

Access the interactive API documentation at http://localhost:8000/docs to explore available endpoints.

## Development Setup

### Prerequisites

- Docker and Docker Compose (latest versions)
- Python 3.11+
- Node.js 18+
- PostgreSQL client tools (psql)
- kubectl (for Kubernetes interaction)

### Local Development with Docker Compose

The included `docker-compose.yml` provides a complete development environment:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f release-manager

# Run tests inside container
docker-compose exec release-manager pytest

# Access database shell
docker-compose exec postgres psql -U release_mgr -d release_manager

# Stop all services
docker-compose down
```

### Environment Configuration

Create a `.env.local` file for local development:

```bash
# Server configuration
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development

# Database
DATABASE_URL=postgresql://release_mgr:password@postgres:5432/release_manager

# Redis cache
REDIS_URL=redis://redis:6379/0

# Kubernetes
KUBECONFIG=/path/to/kubeconfig
K8S_NAMESPACE=development

# External integrations
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
GITHUB_TOKEN=ghp_...
```

### Manual Backend Setup

If you prefer running without Docker:

```bash
# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Initialize database
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Manual Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Access at http://localhost:5173
```

## Project Structure

```
release-manager/
├── README.md                          # This file
├── docker-compose.yml                 # Local development environment
├── Dockerfile                         # Application container image
├── docker-compose.prod.yml            # Production deployment config
│
├── app/                               # Python backend application
│   ├── main.py                        # FastAPI application entry point
│   ├── config.py                      # Configuration management
│   ├── dependencies.py                # Dependency injection
│   │
│   ├── models/                        # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── base.py                    # Base model class
│   │   ├── release.py                 # Release model
│   │   ├── deployment.py              # Deployment model
│   │   ├── user.py                    # User and authentication
│   │   └── audit.py                   # Audit log model
│   │
│   ├── schemas/                       # Pydantic request/response schemas
│   │   ├── release.py
│   │   ├── deployment.py
│   │   └── user.py
│   │
│   ├── api/                           # API route handlers
│   │   ├── v1/
│   │   │   ├── releases.py            # Release endpoints
│   │   │   ├── deployments.py         # Deployment endpoints
│   │   │   ├── users.py               # User management
│   │   │   └── health.py              # Health check endpoints
│   │   └── health.py
│   │
│   ├── services/                      # Business logic
│   │   ├── release_service.py         # Release management
│   │   ├── deployment_service.py      # Deployment orchestration
│   │   ├── kubernetes_service.py      # Kubernetes integration
│   │   ├── notification_service.py    # Slack/Email notifications
│   │   └── audit_service.py           # Audit logging
│   │
│   ├── integrations/                  # External system integrations
│   │   ├── kubernetes.py              # Kubernetes client
│   │   ├── slack.py                   # Slack API integration
│   │   ├── github.py                  # GitHub API integration
│   │   └── prometheus.py              # Prometheus client
│   │
│   ├── utils/                         # Utility functions
│   │   ├── logger.py                  # Logging configuration
│   │   ├── exceptions.py              # Custom exceptions
│   │   └── validators.py              # Input validation
│   │
│   └── database/                      # Database configuration
│       ├── session.py                 # Session management
│       └── base.py                    # Database setup
│
├── alembic/                           # Database migrations
│   ├── versions/                      # Migration files
│   ├── env.py                         # Migration environment
│   └── script.py.mako                 # Migration template
│
├── frontend/                          # React TypeScript frontend
│   ├── src/
│   │   ├── main.tsx                   # Entry point
│   │   ├── App.tsx                    # Root component
│   │   │
│   │   ├── pages/                     # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Releases.tsx
│   │   │   ├── Deployments.tsx
│   │   │   └── AuditLogs.tsx
│   │   │
│   │   ├── components/                # Reusable components
│   │   │   ├── ReleaseSummary.tsx
│   │   │   ├── DeploymentStatus.tsx
│   │   │   └── ReleaseForm.tsx
│   │   │
│   │   ├── hooks/                     # Custom React hooks
│   │   │   └── useApi.ts
│   │   │
│   │   ├── api/                       # API client
│   │   │   └── client.ts
│   │   │
│   │   └── styles/                    # CSS modules
│   │       └── globals.css
│   │
│   ├── public/                        # Static assets
│   ├── package.json
│   └── vite.config.ts
│
├── tests/                             # Test suite
│   ├── unit/                          # Unit tests
│   │   ├── test_release_service.py
│   │   ├── test_deployment_service.py
│   │   └── test_kubernetes_service.py
│   │
│   ├── integration/                   # Integration tests
│   │   ├── test_api_releases.py
│   │   ├── test_api_deployments.py
│   │   └── test_database.py
│   │
│   ├── e2e/                           # End-to-end tests
│   │   ├── test_release_workflow.py
│   │   └── test_deployment_workflow.py
│   │
│   └── conftest.py                    # Pytest configuration
│
├── k8s/                               # Kubernetes manifests
│   ├── release-manager-deployment.yaml
│   ├── release-manager-service.yaml
│   ├── postgres-deployment.yaml
│   ├── redis-deployment.yaml
│   ├── ingress.yaml
│   └── kustomization.yaml
│
├── helm/                              # Helm charts
│   └── release-manager/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── docs/                              # Documentation
│   ├── deployment-guide.md            # Step-by-step deployment
│   ├── rollback-procedure.md          # How to rollback
│   ├── database-migrations.md         # Migration guide
│   ├── incident-response.md           # Incident procedures
│   └── api-reference.md               # API documentation
│
├── scripts/                           # Utility scripts
│   ├── deploy.sh                      # Deployment script
│   ├── rollback.sh                    # Rollback script
│   ├── setup-dev.sh                   # Development setup
│   └── run-tests.sh                   # Test runner
│
├── .github/                           # GitHub configuration
│   └── workflows/                     # CI/CD workflows
│       ├── tests.yml
│       ├── build.yml
│       └── deploy.yml
│
├── requirements.txt                   # Python dependencies
├── requirements-dev.txt               # Development dependencies
├── pyproject.toml                     # Python project config
├── tsconfig.json                      # TypeScript config
└── .gitignore
```

## API Documentation

The Release Manager API follows RESTful conventions and is documented with OpenAPI/Swagger. Access the interactive documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Core API Endpoints

```
GET    /api/v1/health               # Service health check
GET    /api/v1/ready                # Readiness probe

POST   /api/v1/releases             # Create new release
GET    /api/v1/releases             # List all releases
GET    /api/v1/releases/{id}        # Get release details
PATCH  /api/v1/releases/{id}        # Update release
DELETE /api/v1/releases/{id}        # Delete release

POST   /api/v1/releases/{id}/deploy # Deploy release to environment
GET    /api/v1/deployments          # List all deployments
GET    /api/v1/deployments/{id}     # Get deployment status
POST   /api/v1/deployments/{id}/rollback # Rollback deployment

GET    /api/v1/audit-logs           # List audit events
GET    /api/v1/metrics              # Prometheus metrics

POST   /api/v1/auth/login           # User authentication
POST   /api/v1/auth/logout          # User logout
GET    /api/v1/users/me             # Current user profile
```

See [API Reference](./docs/api-reference.md) for complete endpoint documentation.

## Database Schema

Release Manager uses PostgreSQL with the following core tables:

**releases** - Release version and metadata
- id (UUID, primary key)
- version (String, unique)
- description (Text)
- created_by (UUID, foreign key to users)
- created_at (Timestamp)
- released_at (Timestamp, nullable)
- status (Enum: draft, approved, released, cancelled)

**deployments** - Deployment execution history
- id (UUID, primary key)
- release_id (UUID, foreign key)
- environment (Enum: development, staging, production)
- status (Enum: pending, in_progress, succeeded, failed, rolled_back)
- started_at (Timestamp)
- completed_at (Timestamp, nullable)
- deployed_by (UUID, foreign key to users)
- error_message (Text, nullable)

**users** - Team members and authentication
- id (UUID, primary key)
- email (String, unique)
- name (String)
- role (Enum: admin, engineer, viewer)
- created_at (Timestamp)
- last_login (Timestamp, nullable)

**audit_logs** - Complete action history
- id (UUID, primary key)
- action (String)
- resource_type (String)
- resource_id (String)
- user_id (UUID, foreign key)
- changes (JSON)
- created_at (Timestamp)

View the complete schema with relationships at [Database Schema](./docs/database-schema.md).

## Testing

The project includes comprehensive test coverage across unit, integration, and end-to-end tests.

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/test_release_service.py

# Run tests with coverage report
pytest --cov=app --cov-report=html

# Run only integration tests
pytest tests/integration/

# Run tests matching a pattern
pytest -k "test_deployment"
```

### Test Coverage Goals

- Unit tests: 80%+ coverage
- Integration tests: All API endpoints
- E2E tests: Critical user workflows

### Creating Tests

Follow the existing test structure when adding new tests:

```python
import pytest
from app.services import ReleaseService
from tests.conftest import get_test_db

def test_release_creation():
    """Test creating a new release"""
    service = ReleaseService(get_test_db())

    release = service.create_release(
        version="v2024.01.15",
        description="New feature release"
    )

    assert release.version == "v2024.01.15"
    assert release.status == "draft"
```

## Deployment

### Local Development

```bash
docker-compose up -d
```

### Staging Environment

```bash
# See deployment-guide.md for step-by-step instructions
./scripts/deploy.sh staging
```

### Production Environment

```bash
# See deployment-guide.md for step-by-step instructions
./scripts/deploy.sh production
```

**Important**: Always follow the [Deployment Guide](./docs/deployment-guide.md) for production deployments.

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Create a feature branch** from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and write tests
   ```bash
   pytest  # Verify tests pass
   ```

3. **Follow code style**
   - Python: PEP 8, enforced by `black` and `isort`
   - TypeScript: ESLint and Prettier configuration

4. **Create a pull request** with clear description
   - Reference any related issues
   - Include testing instructions
   - List any breaking changes

5. **Code review** process
   - At least 2 approvals required
   - CI/CD pipeline must pass
   - All tests must pass

### Code Style

```bash
# Format Python code
black app/
isort app/

# Format TypeScript code
cd frontend && npm run format
```

### Development Workflow

1. Create issue describing the feature or bug
2. Create feature branch: `git checkout -b feature/issue-123-description`
3. Make changes with test coverage
4. Create pull request with detailed description
5. Address code review feedback
6. Merge to main after approval
7. Code is automatically deployed to staging
8. Schedule production deployment

## License

MIT License - See LICENSE file for details

---

**Last Updated**: January 2024
**Maintained By**: DevOps Team
**Version**: 2024.01.15
