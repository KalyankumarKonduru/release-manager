# Quick Start Guide - Database Setup

## Prerequisites

```bash
# Install required packages
pip install alembic sqlalchemy asyncpg bcrypt
```

## Step 1: Run the Alembic Migration

```bash
cd /sessions/ecstatic-blissful-mayer/release-manager/backend

# Apply all migrations
alembic upgrade head
```

This creates all 12 tables:
- teams, users, environments, services
- releases, deployments, approvals, audit_logs
- rollbacks, runbooks, deployment_metrics, pipeline_stages

## Step 2: Seed Sample Data

```bash
python scripts/seed_data.py
```

This populates the database with:
- 3 teams (Platform, Backend, Frontend)
- 8 users with hashed password "password123"
- 5 services across teams
- 3 environments (Dev, Staging, Prod)
- 10 releases with various statuses
- 8 deployments across environments
- 5 approvals
- 20 audit log entries
- 2 rollbacks
- 3 runbooks
- 8 deployment metrics
- 15 pipeline stages

## Step 3: Import and Use Services

```python
from app.services.audit import AuditService
from app.services.deployment import DeploymentService

# Log an action
await AuditService.log_action(
    db=db,
    user_id=user_id,
    action="create",
    resource_type="release",
    resource_id=release_id,
    metadata={"version": "1.0.0"}
)

# Create a deployment
deployment = await DeploymentService.create_deployment(
    db=db,
    release_id=release_id,
    environment_id=env_id,
    user_id=user_id
)

# Promote a release (with pipeline stages)
deployment = await DeploymentService.promote_release(
    db=db,
    release_id=release_id,
    target_env_id=prod_env_id,
    user_id=user_id
)

# Execute a rollback
rollback = await DeploymentService.execute_rollback(
    db=db,
    deployment_id=deployment_id,
    user_id=user_id,
    reason="Critical bug found"
)

# Get deployment with stages
deployment = await DeploymentService.get_deployment_with_stages(
    db=db,
    deployment_id=deployment_id
)

# Get audit logs
logs, total = await AuditService.get_audit_logs(
    db=db,
    filters={"action": "deploy"},
    limit=50,
    offset=0
)

# Export audit logs to CSV
csv_data = await AuditService.export_audit_logs_csv(
    db=db,
    filters={"resource_type": "deployment"}
)
```

## Database Schema Quick Reference

### Core Tables
- **teams** - Team entities with member counts
- **users** - User accounts with hashed passwords
- **services** - Microservices managed by teams

### Deployment Pipeline
- **releases** - Release versions of services
- **deployments** - Deployment instances to environments
- **environments** - Target deployment environments
- **pipeline_stages** - Individual deployment pipeline stages

### Monitoring & Tracking
- **deployment_metrics** - Performance metrics per deployment
- **approvals** - Approval workflow for deployments
- **audit_logs** - Comprehensive audit trail
- **rollbacks** - Rollback history
- **runbooks** - Operational procedures

## File Locations

```
/sessions/ecstatic-blissful-mayer/release-manager/backend/
├── alembic/
│   └── versions/
│       └── 001_initial_schema.py          # Database migration
├── scripts/
│   └── seed_data.py                       # Seed data script
└── app/
    └── services/
        ├── __init__.py                    # Services package
        ├── audit.py                       # Audit logging service
        └── deployment.py                  # Deployment orchestration service
```

## Environment Variables

```bash
# Set custom database URL
export DATABASE_URL="postgresql://user:password@localhost/release_manager"

# Run seed script with custom database
DATABASE_URL=postgresql://... python scripts/seed_data.py
```

## Reverting the Migration

```bash
# Downgrade to remove all tables
alembic downgrade base
```

## Verification

```bash
# Check migration status
alembic current

# View migration history
alembic history
```

## Common Tasks

### Get all deployments for a service
```python
from sqlalchemy import select
from app.models.deployment import Deployment
from app.models.release import Release

result = await db.execute(
    select(Deployment)
    .join(Release)
    .where(Release.service_id == service_id)
)
deployments = result.scalars().all()
```

### Get audit trail for a resource
```python
logs, _ = await AuditService.get_audit_logs(
    db=db,
    filters={
        "resource_type": "deployment",
        "resource_id": deployment_id
    }
)
```

### Update pipeline stage status
```python
stage = await DeploymentService.update_pipeline_stage(
    db=db,
    stage_id=stage_id,
    status="completed",
    output="Build successful"
)
```

## Testing

All code is async-compatible and ready for use with pytest and async test fixtures.

Example test pattern:
```python
@pytest.mark.asyncio
async def test_create_deployment(db_session):
    deployment = await DeploymentService.create_deployment(
        db=db_session,
        release_id=release_id,
        environment_id=env_id,
        user_id=user_id
    )
    assert deployment.status == "pending"
```

## Troubleshooting

### Migration fails with "table already exists"
- The migration creates tables if they don't exist
- Use `alembic downgrade base` then `alembic upgrade head` to reset

### Seed script fails to connect
- Check DATABASE_URL is set correctly
- Verify PostgreSQL is running
- Ensure database exists: `createdb release_manager`

### Import errors when using services
- Ensure you're in the backend directory
- PYTHONPATH should include the backend directory
- Run migrations before seeding data
