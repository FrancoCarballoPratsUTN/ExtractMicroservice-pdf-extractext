"""Application configuration loaded from the environment."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

DEFAULT_MAX_SIZE_BYTES = 10 * 1024 * 1024


class Settings(BaseSettings):
    """Operational configuration; overridable via environment or ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    max_size_bytes: int = DEFAULT_MAX_SIZE_BYTES


@lru_cache
def get_settings() -> Settings:
    """Return the memoized application settings."""
    return Settings()
