"""Application configuration settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    JWT Configuration:
    - JWT_SECRET_KEY: Secret key for signing tokens (REQUIRED, set via environment)
    - JWT_ALGORITHM: Algorithm for JWT signing (default: HS256)
    - JWT_EXPIRATION_SECONDS: Token lifetime in seconds (default: 3600 = 1 hour)
    - JWT_CLOCK_SKEW_SECONDS: Clock skew tolerance in seconds (default: 300 = 5 minutes)
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    JWT_SECRET_KEY: str  # Must be set via environment variable
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600  # 1 hour
    JWT_CLOCK_SKEW_SECONDS: int = 300  # 5 minutes


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    This function loads settings from environment variables and caches the result.
    Using a function allows the type checker to understand the initialization pattern.
    """
    return Settings()  # type: ignore[call-arg]


# Global settings instance for convenience
settings = get_settings()
