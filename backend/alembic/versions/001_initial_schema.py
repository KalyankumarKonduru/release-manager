"""Initial schema creation - all 12 tables with indexes and constraints.

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-10 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from uuid import uuid4


# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create all tables in proper dependency order."""

    # 1. Teams
    op.execute("""
        CREATE TABLE teams (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            slack_channel VARCHAR(255),
            member_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_teams_name', 'teams', ['name'])
    op.create_index('idx_teams_created_at', 'teams', ['created_at'])

    # 2. Users
    op.execute("""
        CREATE TABLE users (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            email VARCHAR(255) NOT NULL UNIQUE,
            username VARCHAR(50) NOT NULL UNIQUE,
            full_name VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            is_admin BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_username', 'users', ['username'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])

    # 3. Environments
    op.execute("""
        CREATE TABLE environments (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            environment_type VARCHAR(50) NOT NULL,
            config_path VARCHAR(500),
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_environments_name', 'environments', ['name'])
    op.create_index('idx_environments_type', 'environments', ['environment_type'])

    # 4. Services
    op.execute("""
        CREATE TABLE services (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            name VARCHAR(255) NOT NULL UNIQUE,
            description TEXT,
            repository_url VARCHAR(500) NOT NULL,
            team_id UUID NOT NULL REFERENCES teams(id) ON DELETE CASCADE,
            slack_channel VARCHAR(255),
            owner_id UUID REFERENCES users(id) ON DELETE SET NULL,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_services_name', 'services', ['name'])
    op.create_index('idx_services_team_id', 'services', ['team_id'])
    op.create_index('idx_services_owner_id', 'services', ['owner_id'])
    op.create_index('idx_services_created_at', 'services', ['created_at'])

    # 5. Releases
    op.execute("""
        CREATE TABLE releases (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            service_id UUID NOT NULL REFERENCES services(id) ON DELETE CASCADE,
            version VARCHAR(50) NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'draft',
            release_notes TEXT,
            git_commit VARCHAR(255),
            created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(service_id, version)
        )
    """)
    op.create_index('idx_releases_service_id', 'releases', ['service_id'])
    op.create_index('idx_releases_version', 'releases', ['version'])
    op.create_index('idx_releases_status', 'releases', ['status'])
    op.create_index('idx_releases_created_by', 'releases', ['created_by'])

    # 6. Deployments
    op.execute("""
        CREATE TABLE deployments (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            release_id UUID NOT NULL REFERENCES releases(id) ON DELETE CASCADE,
            environment_id UUID NOT NULL REFERENCES environments(id) ON DELETE RESTRICT,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            deployed_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            deployed_at TIMESTAMP,
            completed_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_deployments_release_id', 'deployments', ['release_id'])
    op.create_index('idx_deployments_environment_id', 'deployments', ['environment_id'])
    op.create_index('idx_deployments_status', 'deployments', ['status'])
    op.create_index('idx_deployments_deployed_by', 'deployments', ['deployed_by'])
    op.create_index('idx_deployments_release_env', 'deployments', ['release_id', 'environment_id'])

    # 7. Approvals
    op.execute("""
        CREATE TABLE approvals (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
            approver_id UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            notes TEXT,
            approved_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_approvals_deployment_id', 'approvals', ['deployment_id'])
    op.create_index('idx_approvals_approver_id', 'approvals', ['approver_id'])
    op.create_index('idx_approvals_status', 'approvals', ['status'])

    # 8. Audit Logs
    op.execute("""
        CREATE TABLE audit_logs (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            action VARCHAR(100) NOT NULL,
            resource_type VARCHAR(100) NOT NULL,
            resource_id UUID NOT NULL,
            details JSONB,
            ip_address VARCHAR(50),
            user_agent VARCHAR(500),
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_resource', 'audit_logs', ['resource_type', 'resource_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])

    # 9. Rollbacks
    op.execute("""
        CREATE TABLE rollbacks (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
            target_release_id UUID NOT NULL REFERENCES releases(id) ON DELETE RESTRICT,
            reason TEXT NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            initiated_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            completed_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_rollbacks_deployment_id', 'rollbacks', ['deployment_id'])
    op.create_index('idx_rollbacks_target_release_id', 'rollbacks', ['target_release_id'])
    op.create_index('idx_rollbacks_initiated_by', 'rollbacks', ['initiated_by'])
    op.create_index('idx_rollbacks_status', 'rollbacks', ['status'])

    # 10. Runbooks
    op.execute("""
        CREATE TABLE runbooks (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            title VARCHAR(255) NOT NULL,
            content TEXT NOT NULL,
            service_id UUID REFERENCES services(id) ON DELETE SET NULL,
            environment_id UUID REFERENCES environments(id) ON DELETE SET NULL,
            tags JSONB,
            created_by UUID NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
            is_active BOOLEAN NOT NULL DEFAULT true,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_runbooks_title', 'runbooks', ['title'])
    op.create_index('idx_runbooks_service_id', 'runbooks', ['service_id'])
    op.create_index('idx_runbooks_environment_id', 'runbooks', ['environment_id'])
    op.create_index('idx_runbooks_created_by', 'runbooks', ['created_by'])

    # 11. Deployment Metrics
    op.execute("""
        CREATE TABLE deployment_metrics (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            deployment_id UUID NOT NULL UNIQUE REFERENCES deployments(id) ON DELETE CASCADE,
            metric_name VARCHAR(100) NOT NULL,
            metric_value FLOAT NOT NULL,
            unit VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_deployment_metrics_deployment_id', 'deployment_metrics', ['deployment_id'])
    op.create_index('idx_deployment_metrics_name', 'deployment_metrics', ['metric_name'])

    # 12. Pipeline Stages
    op.execute("""
        CREATE TABLE pipeline_stages (
            id UUID PRIMARY KEY DEFAULT (gen_random_uuid()),
            deployment_id UUID NOT NULL REFERENCES deployments(id) ON DELETE CASCADE,
            name VARCHAR(255) NOT NULL,
            "order" INTEGER NOT NULL,
            status VARCHAR(50) NOT NULL DEFAULT 'pending',
            timeout_seconds INTEGER NOT NULL DEFAULT 3600,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            output TEXT,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)
    op.create_index('idx_pipeline_stages_deployment_id', 'pipeline_stages', ['deployment_id'])
    op.create_index('idx_pipeline_stages_status', 'pipeline_stages', ['status'])


def downgrade() -> None:
    """Drop all tables in reverse dependency order."""

    # Drop in reverse order of creation
    op.execute("DROP TABLE IF EXISTS pipeline_stages CASCADE")
    op.execute("DROP TABLE IF EXISTS deployment_metrics CASCADE")
    op.execute("DROP TABLE IF EXISTS runbooks CASCADE")
    op.execute("DROP TABLE IF EXISTS rollbacks CASCADE")
    op.execute("DROP TABLE IF EXISTS audit_logs CASCADE")
    op.execute("DROP TABLE IF EXISTS approvals CASCADE")
    op.execute("DROP TABLE IF EXISTS deployments CASCADE")
    op.execute("DROP TABLE IF EXISTS releases CASCADE")
    op.execute("DROP TABLE IF EXISTS services CASCADE")
    op.execute("DROP TABLE IF EXISTS environments CASCADE")
    op.execute("DROP TABLE IF EXISTS users CASCADE")
    op.execute("DROP TABLE IF EXISTS teams CASCADE")
