import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    APP_NAME: str = "VariSetu Command Center API"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api"

    # Database connection string
    # Standard PostgreSQL: postgresql+asyncpg://postgres:postgres@localhost:5432/varisetu
    # Supabase PostgreSQL: postgresql+asyncpg://postgres:[password]@db.[ref].supabase.co:5432/postgres
    # SQLite fallback for zero-setup local dev/test: sqlite+aiosqlite:///./varisetu.db
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./varisetu.db",
        description="Async database connection string"
    )

    # Sync Database URL for Alembic migrations if needed
    @property
    def SYNC_DATABASE_URL(self) -> str:
        url = self.DATABASE_URL
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg2").replace("postgresql+psycopg2", "postgresql")
        if "+aiosqlite" in url:
            return url.replace("+aiosqlite", "")
        return url

    # Redis Connection (Optional, falls back to in-memory)
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"

    # Security & JWT Token Config
    JWT_SECRET_KEY: str = "varisetu-super-secret-key-change-in-production-2026"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # When False, allows read/write access without token for prototyping
    AUTH_REQUIRED: bool = False

    # Modular Storage & AI Provider Settings
    STORAGE_PROVIDER: str = "local"
    STORAGE_LOCAL_DIR: str = "./uploads"

    VECTOR_PROVIDER: str = "mock"
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None

    SPEECH_PROVIDER: str = "mock"
    VISION_PROVIDER: str = "mock"
    WEATHER_PROVIDER: str = "mock"
    NOTIFICATION_PROVIDER: str = "mock"

    # CORS Allowed Origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]


settings = Settings()
