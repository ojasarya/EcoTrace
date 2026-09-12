"""Application configuration loaded from environment variables."""

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url


class Settings(BaseSettings):
    """Validated settings for the API and its infrastructure."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        populate_by_name=True,
    )

    app_name: str = Field(default="EcoTrace API", validation_alias="APP_NAME")
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    app_version: str = Field(default="0.1.0", validation_alias="APP_VERSION")
    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")
    database_url: str = Field(validation_alias="DATABASE_URL", repr=False)
    cors_origins: str = Field(
        default="http://localhost:5173",
        validation_alias="CORS_ORIGINS",
    )

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        """Validate the configured database URL without connecting to it."""

        try:
            parsed = make_url(value)
        except (AttributeError, ValueError):
            raise ValueError("DATABASE_URL must be a valid database URL") from None

        if parsed.drivername not in {
            "postgresql",
            "postgresql+psycopg",
            "sqlite",
            "sqlite+pysqlite",
        }:
            raise ValueError(
                "DATABASE_URL must use PostgreSQL or SQLite during local development"
            )
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as normalized values."""

        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide application settings instance."""

    return Settings()
