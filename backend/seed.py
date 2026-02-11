"""Seed script to create demo user on first deploy."""

import asyncio
import os
import sys

# Ensure the backend package is importable
sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import select
from app.core.config import settings
from app.core.database import db
from app.core.security import hash_password
from app.models.user import User


async def seed():
    """Create demo user if it doesn't already exist."""
    await db.initialize()
    await db.create_tables()

    async with db.get_session() as session:
        result = await session.execute(
            select(User).where(User.email == "demo@example.com")
        )
        if result.scalar_one_or_none():
            print("Demo user already exists, skipping seed.")
            return

        user = User(
            email="demo@example.com",
            username="demo",
            full_name="Demo User",
            hashed_password=hash_password("password123"),
            is_active=True,
            is_admin=True,
        )
        session.add(user)
        await session.commit()
        print("Demo user created: demo@example.com / password123")

    await db.close()


if __name__ == "__main__":
    asyncio.run(seed())
