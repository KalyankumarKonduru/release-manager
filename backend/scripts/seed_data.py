#!/usr/bin/env python3
"""Database seeding script for DevOps Release Manager.

This script populates the database with realistic sample data for development and testing.

Usage:
    python scripts/seed_data.py
    DATABASE_URL=postgresql://user:pass@localhost/dbname python scripts/seed_data.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from uuid import uuid4

import asyncpg
import bcrypt


# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/release_manager")


async def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt).decode()


async def seed_database() -> None:
    """Seed the database with sample data."""
    try:
        # Parse database URL
        # Handle both postgresql:// and postgres:// formats
        db_url = DATABASE_URL.replace("postgresql://", "postgres://")

        conn = await asyncpg.connect(db_url)
        print("Connected to database successfully")

        # Helper function to generate timestamps in the last 30 days
        base_time = datetime.utcnow()

        def get_timestamp(days_ago: int = 0, hours_ago: int = 0, minutes_ago: int = 0) -> datetime:
            return base_time - timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)

        # Generate UUIDs for all records
        team_ids = {
            "platform": str(uuid4()),
            "backend": str(uuid4()),
            "frontend": str(uuid4()),
        }

        user_ids = {
            "admin": str(uuid4()),
            "lead1": str(uuid4()),
            "lead2": str(uuid4()),
            "dev1": str(uuid4()),
            "dev2": str(uuid4()),
            "dev3": str(uuid4()),
            "viewer1": str(uuid4()),
            "viewer2": str(uuid4()),
        }

        service_ids = {
            "auth": str(uuid4()),
            "payment": str(uuid4()),
            "dashboard": str(uuid4()),
            "gateway": str(uuid4()),
            "notification": str(uuid4()),
        }

        env_ids = {
            "dev": str(uuid4()),
            "staging": str(uuid4()),
            "prod": str(uuid4()),
        }

        release_ids = [str(uuid4()) for _ in range(10)]
        deployment_ids = [str(uuid4()) for _ in range(8)]
        approval_ids = [str(uuid4()) for _ in range(5)]
        rollback_ids = [str(uuid4()) for _ in range(2)]
        runbook_ids = [str(uuid4()) for _ in range(3)]
        metric_ids = [str(uuid4()) for _ in range(8)]
        stage_ids = [str(uuid4()) for _ in range(15)]

        print("\nSeeding teams...")
        await conn.executemany(
            """
            INSERT INTO teams (id, name, description, slack_channel, member_count, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            [
                (
                    team_ids["platform"],
                    "Platform",
                    "Platform engineering and infrastructure",
                    "#team-platform",
                    4,
                    get_timestamp(days_ago=25),
                    get_timestamp(days_ago=25),
                ),
                (
                    team_ids["backend"],
                    "Backend",
                    "Backend services and APIs",
                    "#team-backend",
                    3,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
                (
                    team_ids["frontend"],
                    "Frontend",
                    "Frontend and UI development",
                    "#team-frontend",
                    2,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
            ],
        )

        print("Seeding users...")
        password_hash = await hash_password("password123")
        await conn.executemany(
            """
            INSERT INTO users (id, email, username, full_name, hashed_password, is_active, is_admin, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            [
                (
                    user_ids["admin"],
                    "admin@example.com",
                    "admin",
                    "Admin User",
                    password_hash,
                    True,
                    True,
                    get_timestamp(days_ago=30),
                    get_timestamp(days_ago=30),
                ),
                (
                    user_ids["lead1"],
                    "lead1@example.com",
                    "lead1",
                    "John Doe",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=25),
                    get_timestamp(days_ago=25),
                ),
                (
                    user_ids["lead2"],
                    "lead2@example.com",
                    "lead2",
                    "Jane Smith",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=25),
                    get_timestamp(days_ago=25),
                ),
                (
                    user_ids["dev1"],
                    "dev1@example.com",
                    "dev1",
                    "Bob Johnson",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
                (
                    user_ids["dev2"],
                    "dev2@example.com",
                    "dev2",
                    "Alice Williams",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
                (
                    user_ids["dev3"],
                    "dev3@example.com",
                    "dev3",
                    "Charlie Brown",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=15),
                    get_timestamp(days_ago=15),
                ),
                (
                    user_ids["viewer1"],
                    "viewer1@example.com",
                    "viewer1",
                    "Diana Ross",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=10),
                    get_timestamp(days_ago=10),
                ),
                (
                    user_ids["viewer2"],
                    "viewer2@example.com",
                    "viewer2",
                    "Eve Taylor",
                    password_hash,
                    True,
                    False,
                    get_timestamp(days_ago=10),
                    get_timestamp(days_ago=10),
                ),
            ],
        )

        print("Seeding environments...")
        await conn.executemany(
            """
            INSERT INTO environments (id, name, description, environment_type, config_path, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            [
                (
                    env_ids["dev"],
                    "Development",
                    "Development environment",
                    "development",
                    "/config/dev",
                    True,
                    get_timestamp(days_ago=30),
                    get_timestamp(days_ago=30),
                ),
                (
                    env_ids["staging"],
                    "Staging",
                    "Staging environment for testing",
                    "staging",
                    "/config/staging",
                    True,
                    get_timestamp(days_ago=30),
                    get_timestamp(days_ago=30),
                ),
                (
                    env_ids["prod"],
                    "Production",
                    "Production environment",
                    "production",
                    "/config/prod",
                    True,
                    get_timestamp(days_ago=30),
                    get_timestamp(days_ago=30),
                ),
            ],
        )

        print("Seeding services...")
        await conn.executemany(
            """
            INSERT INTO services (id, name, description, repository_url, team_id, slack_channel, owner_id, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            [
                (
                    service_ids["auth"],
                    "auth-service",
                    "Authentication and authorization service",
                    "https://github.com/org/auth-service",
                    team_ids["backend"],
                    "#service-auth",
                    user_ids["lead1"],
                    True,
                    get_timestamp(days_ago=25),
                    get_timestamp(days_ago=25),
                ),
                (
                    service_ids["payment"],
                    "payment-api",
                    "Payment processing API",
                    "https://github.com/org/payment-api",
                    team_ids["backend"],
                    "#service-payment",
                    user_ids["lead1"],
                    True,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
                (
                    service_ids["dashboard"],
                    "user-dashboard",
                    "User dashboard application",
                    "https://github.com/org/user-dashboard",
                    team_ids["frontend"],
                    "#service-dashboard",
                    user_ids["lead2"],
                    True,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
                (
                    service_ids["gateway"],
                    "api-gateway",
                    "API Gateway for service routing",
                    "https://github.com/org/api-gateway",
                    team_ids["platform"],
                    "#service-gateway",
                    user_ids["admin"],
                    True,
                    get_timestamp(days_ago=25),
                    get_timestamp(days_ago=25),
                ),
                (
                    service_ids["notification"],
                    "notification-service",
                    "Notification and messaging service",
                    "https://github.com/org/notification-service",
                    team_ids["backend"],
                    "#service-notification",
                    user_ids["dev1"],
                    True,
                    get_timestamp(days_ago=15),
                    get_timestamp(days_ago=15),
                ),
            ],
        )

        print("Seeding releases...")
        releases_data = [
            (release_ids[0], service_ids["auth"], "1.0.0", "completed", "Initial release", "abc123def456", user_ids["lead1"], get_timestamp(days_ago=20)),
            (release_ids[1], service_ids["auth"], "1.0.1", "completed", "Bug fix release", "abc123def457", user_ids["dev1"], get_timestamp(days_ago=18)),
            (release_ids[2], service_ids["payment"], "2.1.0", "completed", "New payment methods", "def456ghi789", user_ids["lead1"], get_timestamp(days_ago=15)),
            (release_ids[3], service_ids["payment"], "2.1.1", "in-progress", "Performance improvements", "def456ghi790", user_ids["dev2"], get_timestamp(days_ago=5)),
            (release_ids[4], service_ids["dashboard"], "3.0.0", "completed", "UI redesign", "ghi789jkl012", user_ids["lead2"], get_timestamp(days_ago=10)),
            (release_ids[5], service_ids["gateway"], "1.5.0", "completed", "Enhanced routing", "jkl012mno345", user_ids["admin"], get_timestamp(days_ago=12)),
            (release_ids[6], service_ids["notification"], "0.5.0", "draft", "Work in progress", "mno345pqr678", user_ids["dev3"], get_timestamp(days_ago=3)),
            (release_ids[7], service_ids["auth"], "1.1.0", "testing", "New MFA support", "abc123def458", user_ids["dev1"], get_timestamp(days_ago=7)),
            (release_ids[8], service_ids["dashboard"], "3.0.1", "completed", "Bug fixes", "ghi789jkl013", user_ids["dev3"], get_timestamp(days_ago=8)),
            (release_ids[9], service_ids["notification"], "0.4.0", "completed", "Email templates", "mno345pqr677", user_ids["lead1"], get_timestamp(days_ago=20)),
        ]

        await conn.executemany(
            """
            INSERT INTO releases (id, service_id, version, status, release_notes, git_commit, created_by, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            [(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[7]) for r in releases_data],
        )

        print("Seeding deployments...")
        deployments_data = [
            (deployment_ids[0], release_ids[0], env_ids["dev"], "completed", user_ids["lead1"], get_timestamp(days_ago=19, hours_ago=2), get_timestamp(days_ago=19)),
            (deployment_ids[1], release_ids[0], env_ids["staging"], "completed", user_ids["dev1"], get_timestamp(days_ago=17, hours_ago=1), get_timestamp(days_ago=17)),
            (deployment_ids[2], release_ids[1], env_ids["prod"], "completed", user_ids["admin"], get_timestamp(days_ago=15, hours_ago=5), get_timestamp(days_ago=15)),
            (deployment_ids[3], release_ids[2], env_ids["staging"], "completed", user_ids["lead1"], get_timestamp(days_ago=12, hours_ago=3), get_timestamp(days_ago=12)),
            (deployment_ids[4], release_ids[4], env_ids["dev"], "completed", user_ids["lead2"], get_timestamp(days_ago=9, hours_ago=2), get_timestamp(days_ago=9)),
            (deployment_ids[5], release_ids[5], env_ids["staging"], "in-progress", user_ids["admin"], get_timestamp(hours_ago=4), None),
            (deployment_ids[6], release_ids[8], env_ids["prod"], "completed", user_ids["dev3"], get_timestamp(days_ago=7, hours_ago=1), get_timestamp(days_ago=7)),
            (deployment_ids[7], release_ids[9], env_ids["dev"], "completed", user_ids["lead1"], get_timestamp(days_ago=19, hours_ago=3), get_timestamp(days_ago=19)),
        ]

        await conn.executemany(
            """
            INSERT INTO deployments (id, release_id, environment_id, status, deployed_by, deployed_at, completed_at, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            [(d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[5] if d[5] else get_timestamp(hours_ago=4), d[5] if d[5] else get_timestamp(hours_ago=4)) for d in deployments_data],
        )

        print("Seeding approvals...")
        approvals_data = [
            (approval_ids[0], deployment_ids[0], user_ids["admin"], "approved", "Looks good", get_timestamp(days_ago=19)),
            (approval_ids[1], deployment_ids[1], user_ids["lead1"], "approved", "Ready for prod", get_timestamp(days_ago=17)),
            (approval_ids[2], deployment_ids[2], user_ids["admin"], "approved", "Approved", get_timestamp(days_ago=15)),
            (approval_ids[3], deployment_ids[3], user_ids["lead2"], "approved", "Verified", get_timestamp(days_ago=12)),
            (approval_ids[4], deployment_ids[5], user_ids["admin"], "pending", "Awaiting approval", None),
        ]

        await conn.executemany(
            """
            INSERT INTO approvals (id, deployment_id, approver_id, status, notes, approved_at, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            [(a[0], a[1], a[2], a[3], a[4], a[5], get_timestamp(days_ago=abs(int(a[5].day - base_time.day)) if a[5] else 0) if a[5] else get_timestamp(hours_ago=1),
              get_timestamp(days_ago=abs(int(a[5].day - base_time.day)) if a[5] else 0) if a[5] else get_timestamp(hours_ago=1)) for a in approvals_data],
        )

        print("Seeding rollbacks...")
        await conn.executemany(
            """
            INSERT INTO rollbacks (id, deployment_id, target_release_id, reason, status, initiated_by, completed_at, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            [
                (
                    rollback_ids[0],
                    deployment_ids[2],
                    release_ids[0],
                    "Critical bug discovered in production",
                    "completed",
                    user_ids["admin"],
                    get_timestamp(days_ago=14),
                    get_timestamp(days_ago=14, hours_ago=2),
                    get_timestamp(days_ago=14),
                ),
                (
                    rollback_ids[1],
                    deployment_ids[3],
                    release_ids[2],
                    "Performance degradation",
                    "completed",
                    user_ids["lead1"],
                    get_timestamp(days_ago=10),
                    get_timestamp(days_ago=10, hours_ago=1),
                    get_timestamp(days_ago=10),
                ),
            ],
        )

        print("Seeding audit logs...")
        audit_logs = []
        actions = ["create", "update", "delete", "deploy", "approve", "rollback"]
        resource_types = ["release", "deployment", "service", "approval", "user"]

        for i in range(20):
            audit_logs.append((
                str(uuid4()),
                user_ids[list(user_ids.keys())[i % len(user_ids)]],
                actions[i % len(actions)],
                resource_types[i % len(resource_types)],
                str(uuid4()),
                json.dumps({"action": actions[i % len(actions)], "status": "success"}),
                f"192.168.1.{i + 1}",
                "Mozilla/5.0 (X11; Linux x86_64)",
                get_timestamp(days_ago=i % 30),
            ))

        await conn.executemany(
            """
            INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            """,
            audit_logs,
        )

        print("Seeding runbooks...")
        await conn.executemany(
            """
            INSERT INTO runbooks (id, title, content, service_id, environment_id, tags, created_by, is_active, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            """,
            [
                (
                    runbook_ids[0],
                    "Deployment Guide",
                    "# Deployment Guide\n\n1. Ensure all tests pass\n2. Create a release tag\n3. Push to repository\n4. Monitor deployment metrics",
                    service_ids["auth"],
                    None,
                    json.dumps(["deployment", "guide"]),
                    user_ids["lead1"],
                    True,
                    get_timestamp(days_ago=25),
                    get_timestamp(days_ago=25),
                ),
                (
                    runbook_ids[1],
                    "Rollback Procedure",
                    "# Rollback Procedure\n\n1. Identify the issue\n2. Select previous stable version\n3. Execute rollback command\n4. Verify service health",
                    service_ids["gateway"],
                    None,
                    json.dumps(["rollback", "emergency"]),
                    user_ids["admin"],
                    True,
                    get_timestamp(days_ago=20),
                    get_timestamp(days_ago=20),
                ),
                (
                    runbook_ids[2],
                    "Incident Response",
                    "# Incident Response\n\n1. Alert team members\n2. Gather metrics\n3. Root cause analysis\n4. Implement fix\n5. Post-mortem",
                    None,
                    env_ids["prod"],
                    json.dumps(["incident", "response"]),
                    user_ids["admin"],
                    True,
                    get_timestamp(days_ago=15),
                    get_timestamp(days_ago=15),
                ),
            ],
        )

        print("Seeding deployment metrics...")
        metrics_data = [
            (metric_ids[0], deployment_ids[0], "duration_seconds", 45.5, "seconds"),
            (metric_ids[1], deployment_ids[0], "cpu_usage", 75.2, "percent"),
            (metric_ids[2], deployment_ids[1], "duration_seconds", 62.1, "seconds"),
            (metric_ids[3], deployment_ids[1], "memory_usage", 512.8, "MB"),
            (metric_ids[4], deployment_ids[2], "duration_seconds", 88.3, "seconds"),
            (metric_ids[5], deployment_ids[3], "duration_seconds", 55.7, "seconds"),
            (metric_ids[6], deployment_ids[4], "duration_seconds", 40.2, "seconds"),
            (metric_ids[7], deployment_ids[6], "duration_seconds", 71.5, "seconds"),
        ]

        await conn.executemany(
            """
            INSERT INTO deployment_metrics (id, deployment_id, metric_name, metric_value, unit, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            [(m[0], m[1], m[2], m[3], m[4], get_timestamp(), get_timestamp()) for m in metrics_data],
        )

        print("Seeding pipeline stages...")
        stages_data = []
        stage_names = ["build", "test", "security_scan", "deploy", "smoke_test"]

        for i, deployment_id in enumerate(deployment_ids[:8]):
            for j, stage_name in enumerate(stage_names[:3]):  # 3 stages per deployment
                stages_data.append((
                    stage_ids[i * 3 + j],
                    deployment_id,
                    stage_name,
                    j,
                    "completed" if i < 7 else "in-progress",
                    3600,
                    get_timestamp(days_ago=(8 - i) if i < 7 else 0, hours_ago=2),
                    get_timestamp(days_ago=(8 - i) if i < 7 else 0, hours_ago=1) if i < 7 else None,
                    f"Stage {stage_name} completed successfully" if i < 7 else None,
                ))

        await conn.executemany(
            """
            INSERT INTO pipeline_stages (id, deployment_id, name, "order", status, timeout_seconds, started_at, completed_at, output, created_at, updated_at)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
            """,
            [(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], s[8], s[6], s[6]) for s in stages_data],
        )

        print("\n✅ Database seeded successfully!")
        print(f"  - Teams: 3")
        print(f"  - Users: 8")
        print(f"  - Services: 5")
        print(f"  - Environments: 3")
        print(f"  - Releases: 10")
        print(f"  - Deployments: 8")
        print(f"  - Approvals: 5")
        print(f"  - Audit Logs: 20")
        print(f"  - Rollbacks: 2")
        print(f"  - Runbooks: 3")
        print(f"  - Deployment Metrics: 8")
        print(f"  - Pipeline Stages: {len(stages_data)}")

        await conn.close()

    except Exception as e:
        print(f"❌ Error seeding database: {str(e)}", file=sys.stderr)
        raise


if __name__ == "__main__":
    asyncio.run(seed_database())
