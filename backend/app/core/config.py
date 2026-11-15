import json
from functools import lru_cache
from typing import Annotated, Any

from pydantic import BeforeValidator, Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _parse_origins(v: Any) -> list[str]:
    if isinstance(v, str) and not v.startswith("["):
        return [i.strip() for i in v.split(",") if i.strip()]
    elif isinstance(v, str) and v.startswith("["):
        try:
            parsed = json.loads(v)
            if isinstance(parsed, list):
                return [str(item) for item in parsed]
        except Exception:
            pass
    elif isinstance(v, list):
        return [str(item) for item in v]
    return ["http://localhost:3000", "http://localhost:5173"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Application settings
    PROJECT_NAME: str = "Get Idiomas AI Writing System"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # PostgreSQL Database settings
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "get_idiomas"
    DATABASE_URL: str | None = None
    DB_ECHO: bool = False

    # Redis Cache & Broker settings
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS settings
    ALLOWED_ORIGINS: Annotated[list[str], BeforeValidator(_parse_origins)] = Field(
        default=["http://localhost:3000", "http://localhost:5173"]
    )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            # Ensure asyncpg dialect is specified if standard postgresql:// is provided
            if self.DATABASE_URL.startswith("postgresql://"):
                return self.DATABASE_URL.replace(
                    "postgresql://", "postgresql+asyncpg://", 1
                )
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
