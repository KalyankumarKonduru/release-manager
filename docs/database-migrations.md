# Database Migrations Guide

## Overview

This guide covers the complete lifecycle of database migrations using Alembic, from creation through application to rollback. All migrations are version controlled and can be reviewed before execution.

## Creating New Migrations

### Using Alembic Auto-Generate

The recommended approach is to use Alembic's auto-generation feature to create migrations from model changes:

```bash
# First, update your SQLAlchemy models in app/models/
# Then generate migration file:

alembic revision --autogenerate -m "Add user_roles table"

# This creates a new file in alembic/versions/ like:
# 9c2b3f1a4e5d_add_user_roles_table.py
```

### Manual Migration Creation

For complex schema changes, create migrations manually:

```bash
# Create empty migration file
alembic revision -m "Custom schema change"

# Open the generated file in alembic/versions/
# Implement the upgrade() and downgrade() functions manually
```

### Migration File Structure

Every migration file contains two functions:

```python
"""Add user_roles table

Revision ID: 9c2b3f1a4e5d
Revises: 8f1a2b3c4d5e
Create Date: 2024-01-15 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# Migration metadata
revision = '9c2b3f1a4e5d'
down_revision = '8f1a2b3c4d5e'
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Apply migration forward"""
    op.create_table(
        'user_roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_user_roles_user_id', 'user_roles', ['user_id'])

def downgrade() -> None:
    """Revert migration"""
    op.drop_index('ix_user_roles_user_id', table_name='user_roles')
    op.drop_table('user_roles')
```

## Best Practices for Migration Writing

**Always Include Downgrade Logic**

Every `upgrade()` must have a corresponding `downgrade()` that completely reverses the change. This ensures you can rollback if needed.

```python
def upgrade() -> None:
    op.add_column('users', sa.Column('email_verified', sa.Boolean(), nullable=False, server_default='false'))

def downgrade() -> None:
    op.drop_column('users', 'email_verified')
```

**Data Transformations Require Care**

When transforming existing data, create intermediate migrations:

```python
def upgrade() -> None:
    # Step 1: Add new column with default
    op.add_column('deployments', sa.Column('status', sa.String(20), nullable=False, server_default='pending'))

    # Step 2: Update existing rows (do this in smaller batches for large tables)
    op.execute("""
        UPDATE deployments SET status = 'completed'
        WHERE completed_at IS NOT NULL
    """)

    # Step 3: Remove server default to make it required
    op.alter_column('deployments', 'status', server_default=None)

def downgrade() -> None:
    op.drop_column('deployments', 'status')
```

**Avoid Raw SQL When Possible**

Use SQLAlchemy constructs for portability across databases:

```python
# Good - works with PostgreSQL, MySQL, SQLite
op.create_table('events', ...)

# Avoid - PostgreSQL specific
op.execute("""CREATE UNLOGGED TABLE events AS ...""")
```

**Test Performance-Critical Operations**

For large tables, test migration performance:

```python
def upgrade() -> None:
    # Adding index to large table - test for lock time
    op.create_index('ix_deployments_created_at', 'deployments', ['created_at'])

    # Create in background (PostgreSQL specific)
    op.execute("""CREATE INDEX CONCURRENTLY ix_deployments_status ON deployments(status)""")

def downgrade() -> None:
    op.drop_index('ix_deployments_status')
    op.drop_index('ix_deployments_created_at')
```

## Testing Migrations Locally

Before deploying to any environment, test migrations thoroughly on your local development machine:

### Setup Local Database

```bash
# Start local PostgreSQL with Docker
docker-compose up -d postgres

# Verify connection
psql postgresql://user:password@localhost/release_manager

# Initialize schema
alembic upgrade head
```

### Test Forward Migration

```bash
# Check current migration version
alembic current

# Apply the new migration
alembic upgrade +1

# Verify table/column was created
psql -c "SELECT * FROM information_schema.tables WHERE table_name='user_roles';"
```

### Test Backward Migration

```bash
# Downgrade one migration
alembic downgrade -1

# Verify previous state
psql -c "SELECT * FROM information_schema.tables WHERE table_name='user_roles';"

# Should return empty result
```

### Verify Data Integrity

For migrations involving data changes, verify data consistency:

```python
# Create test file: test_migration_9c2b3f1a4e5d.py

import pytest
from app.models import UserRole, User
from app.database import SessionLocal

def test_user_roles_migration():
    """Verify user_roles migration creates correct schema"""
    session = SessionLocal()

    # Create test data
    user = User(name="Test User", email="test@example.com")
    session.add(user)
    session.commit()

    # Create role relationship
    role = UserRole(user_id=user.id, role="admin")
    session.add(role)
    session.commit()

    # Verify data
    retrieved_role = session.query(UserRole).filter_by(user_id=user.id).first()
    assert retrieved_role is not None
    assert retrieved_role.role == "admin"

    session.close()

# Run test
pytest test_migration_9c2b3f1a4e5d.py
```

## Applying Migrations to Staging

After local testing, apply migrations to staging environment:

```bash
# 1. Verify staging database backup completed
kubectl exec -it $(kubectl get pod -l app=db-staging -n staging \
  -o jsonpath='{.items[0].metadata.name}') -n staging \
  -- pg_dump -U postgres release_manager > /backups/staging-pre-migration.sql

# 2. Apply migration to staging
POD_NAME=$(kubectl get pod -l app=release-manager -n staging \
  -o jsonpath='{.items[0].metadata.name}')

kubectl exec -it $POD_NAME -n staging -- alembic upgrade head

# 3. Verify migration applied
kubectl exec -it $POD_NAME -n staging -- alembic current

# 4. Run full test suite on staging
./tests/integration-tests.sh --environment staging

# 5. Monitor for 30 minutes
# Watch logs for any migration-related errors
kubectl logs deployment/release-manager-staging -n staging -f
```

## Applying Migrations to Production

Production migrations require careful planning and execution:

### Pre-Production Checklist

- [ ] Migration tested on local development database
- [ ] Migration tested on staging environment
- [ ] Full backup of production database taken
- [ ] Maintenance window scheduled (if needed)
- [ ] Rollback plan reviewed and tested
- [ ] Team notified of migration window
- [ ] On-call engineer confirmed and available

### Safe Production Migration Execution

```bash
# 1. Create pre-migration backup
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
kubectl exec -it $(kubectl get pod -l app=db -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production \
  -- pg_dump -U postgres release_manager > /backups/prod-pre-migration-${TIMESTAMP}.sql

# Compress backup for storage
gzip /backups/prod-pre-migration-${TIMESTAMP}.sql

# 2. Get production pod name
POD_NAME=$(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}')

# 3. Show migration SQL before executing (for audit)
kubectl exec -it $POD_NAME -n production -- alembic upgrade head --sql

# 4. Apply migration with monitoring
kubectl exec -it $POD_NAME -n production -- alembic upgrade head

# 5. Verify migration version
kubectl exec -it $POD_NAME -n production -- alembic current

# 6. Monitor application and database metrics for 60 minutes
# Watch for:
# - Database query performance degradation
# - Increased connection count
# - Lock wait times
# - Application error rate
```

### Large Table Migrations

For tables with millions of rows, use non-blocking operations:

```python
def upgrade() -> None:
    # Create new column without lock
    op.add_column('large_table',
        sa.Column('new_column', sa.String(100), nullable=True),
        schema=None)

    # Update in batches to avoid long locks
    op.execute("""
        DO $$
        BEGIN
            FOR counter IN 1..10 LOOP
                UPDATE large_table
                SET new_column = 'default_value'
                WHERE new_column IS NULL
                LIMIT 100000;
                COMMIT;
            END LOOP;
        END $$;
    """)

    # Add NOT NULL constraint
    op.alter_column('large_table', 'new_column', nullable=False)

def downgrade() -> None:
    op.drop_column('large_table', 'new_column')
```

## Rolling Back Migrations

### Manual Migration Rollback

If a migration causes issues, revert it:

```bash
# 1. Connect to database pod
POD_NAME=$(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}')

# 2. Check current migration version
kubectl exec -it $POD_NAME -n production -- alembic current

# 3. Revert to previous migration
kubectl exec -it $POD_NAME -n production -- alembic downgrade -1

# 4. Verify reverted state
kubectl exec -it $POD_NAME -n production -- alembic current

# 5. Check database schema matches previous version
kubectl exec -it $POD_NAME -n production -- \
  psql -U postgres -d release_manager -c "\dt"
```

### From Backup (Last Resort)

If migration corrupted data and rollback isn't possible:

```bash
# 1. Restore from pre-migration backup
BACKUP_FILE="/backups/prod-pre-migration-20240115_143000.sql.gz"

gunzip -c $BACKUP_FILE | kubectl exec -i $(kubectl get pod -l app=db -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production \
  -- psql -U postgres

# 2. Verify data restored
kubectl exec -it $(kubectl get pod -l app=db -n production \
  -o jsonpath='{.items[0].metadata.name}') -n production \
  -- psql -U postgres -d release_manager -c "SELECT COUNT(*) FROM users;"

# 3. Check migration version
POD_NAME=$(kubectl get pod -l app=release-manager -n production \
  -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $POD_NAME -n production -- alembic current
```

## Schema Change Best Practices

**Use Minimal Migrations**

Keep each migration focused on a single logical change:

```python
# Good - one concern per migration
# Migration 1: Add new table
# Migration 2: Populate new table from old table
# Migration 3: Drop old table

# Avoid - multiple unrelated changes
# Migration: Add table, rename column, add index, modify constraint
```

**Add Comments for Complex Changes**

Document the reasoning behind schema decisions:

```python
def upgrade() -> None:
    # Using JSONB for flexible schema storage
    # Allows deployment metadata to evolve without schema changes
    op.add_column('releases',
        sa.Column('metadata', sa.JSON(), nullable=True),
        comment='Flexible storage for deployment-specific metadata')
```

**Plan for Rollback from Day One**

Always write downgrade() assuming the migration might need to be reverted:

```python
def upgrade() -> None:
    op.rename_table('old_name', 'new_name')

def downgrade() -> None:
    op.rename_table('new_name', 'old_name')
```

**Index Large Tables**

Add indexes for columns frequently used in WHERE clauses:

```python
def upgrade() -> None:
    op.create_table('releases', ...)
    op.create_index('ix_releases_status', 'releases', ['status'])
    op.create_index('ix_releases_created_at', 'releases', ['created_at'])

def downgrade() -> None:
    op.drop_index('ix_releases_created_at')
    op.drop_index('ix_releases_status')
    op.drop_table('releases')
```

## Common Pitfalls and Solutions

**Pitfall: Missing Foreign Key Constraint**

```python
# Problem - column created without constraint
op.add_column('deployments', sa.Column('release_id', sa.Integer()))

# Solution - always add constraint
op.add_column('deployments', sa.Column('release_id', sa.Integer()))
op.create_foreign_key('fk_deployments_release_id', 'deployments', 'releases',
                      local_cols=['release_id'], remote_side=['id'])
```

**Pitfall: NULL Values in New NOT NULL Column**

```python
# Problem - causes migration to fail if existing data
op.add_column('users', sa.Column('status', sa.String(20), nullable=False))

# Solution - add as nullable, populate, then remove nullable
op.add_column('users', sa.Column('status', sa.String(20), nullable=True))
op.execute("UPDATE users SET status = 'active' WHERE status IS NULL")
op.alter_column('users', 'status', nullable=False)
```

**Pitfall: Large Index Operations During Production**

```python
# Problem - creates long lock on table
op.create_index('ix_large_table_column', 'large_table', ['column'])

# Solution - use CONCURRENTLY in PostgreSQL
op.execute('CREATE INDEX CONCURRENTLY ix_large_table_column ON large_table(column)')
```

**Pitfall: Not Testing Downgrade**

Always test both directions:

```bash
# Apply migration
alembic upgrade +1

# Test downgrade
alembic downgrade -1

# Verify previous state
alembic current  # Should show previous version
```

## Monitoring Migrations

After applying migrations, monitor these metrics:

```bash
# Database query performance
SELECT query, mean_time, calls
FROM pg_stat_statements
ORDER BY mean_time DESC LIMIT 10;

# Table size changes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

# Index efficiency
SELECT indexname, idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Related Documentation

- [Deployment Guide](./deployment-guide.md) - How migrations integrate with deployments
- [Rollback Procedure](./rollback-procedure.md) - How to rollback migrations if needed
- [Incident Response Guide](./incident-response.md) - Handling migration-related incidents
