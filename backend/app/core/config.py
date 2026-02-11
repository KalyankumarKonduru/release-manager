"""
Application configuration using Pydantic Settings.

This module defines all environment-based and application configuration settings.
It uses Pydantic v2 settings management for validation and type safety.
"""

from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings management.

    Settings are loaded from environment variables with the APP_ prefix.
    Example: APP_DEBUG=true for setting debug mode.
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
        """Pydantic configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return self.DATABASE_URL

    @property
    def redis_url(self) -> str:
        """Get the Redis URL."""
        return self.REDIS_URL


settings = Settings()
