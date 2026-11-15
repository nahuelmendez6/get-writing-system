from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "Get Idiomas AI Evaluation Service"
    VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Internal API security
    INTERNAL_API_KEY: str | None = None

    # LLM Settings
    LLM_PROVIDER: Literal["mock", "openai", "anthropic", "gemini"] = "mock"
    LLM_MODEL_NAME: str = "gpt-4o"
    LLM_TEMPERATURE: float = 0.2
    LLM_TIMEOUT_SECONDS: int = 45

    # Privacy & Zero Data Retention
    ENFORCE_ZDR: bool = True
    SANITIZE_PII: bool = True

    # AI Text Detection Settings
    AI_DETECTION_THRESHOLD: float = 0.70


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
