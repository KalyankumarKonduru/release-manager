"""
Application configuration using Pydantic Settings.

This module defines all environment-based and application configuration settings.
It uses Pydantic v2 settings management for validation and type safety.
"""

from typing import Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings management.

    Settings are loaded from environment variables.
    """

    # Application
    APP_NAME: str = "DevOps Release Manager"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: list[str] = ["*"]

    # Database Configuration
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/release_manager"
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 0

    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_TIMEOUT: int = 300

    # JWT/Security Configuration
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS Configuration
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # GCP Configuration (Optional)
    GCP_PROJECT_ID: Optional[str] = None
    GCP_REGION: Optional[str] = None

    # Logging Configuration
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @model_validator(mode="after")
    def fix_database_url_scheme(self) -> "Settings":
        """Convert Render's postgresql:// to postgresql+asyncpg://."""
        url = self.DATABASE_URL
        if url.startswith("postgres://"):
            self.DATABASE_URL = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            self.DATABASE_URL = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return self


settings = Settings()
