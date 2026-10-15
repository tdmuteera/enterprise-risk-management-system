"""
Configuration management for ERM Backend.
Loads environment variables from .env file using pydantic-settings.
"""

from __future__ import annotations

import logging
from typing import List, Literal, Optional, Union

from pydantic import AliasChoices, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = Field(default="ERM Platform", validation_alias=AliasChoices("APP_NAME", "app_name"))
    app_version: str = Field(default="1.0.0", validation_alias=AliasChoices("APP_VERSION", "app_version"))

    environment: Literal["development", "production"] = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "environment"),
    )
    debug: bool = Field(default=False, validation_alias=AliasChoices("DEBUG", "debug"))

    db_url: str = Field(
        default="postgresql+asyncpg://user:password@localhost:5432/erm_db",
        validation_alias=AliasChoices("DATABASE_URL", "DB_URL", "db_url"),
    )

    secret_key: str = Field(
        default="your-super-secret-key-change-in-production",
        validation_alias=AliasChoices("SECRET_KEY", "secret_key"),
    )
    algorithm: str = Field(default="HS256", validation_alias=AliasChoices("ALGORITHM", "algorithm"))
    access_token_expire_minutes: int = Field(
        default=480,
        validation_alias=AliasChoices("ACCESS_TOKEN_EXPIRE_MINUTES", "access_token_expire_minutes"),
    )
    refresh_token_expire_days: int = Field(
        default=30,
        validation_alias=AliasChoices("REFRESH_TOKEN_EXPIRE_DAYS", "refresh_token_expire_days"),
    )

    cors_origins: Union[str, List[str]] = Field(
        default_factory=lambda: ["http://localhost:5173"],
        validation_alias=AliasChoices("CORS_ORIGINS", "cors_origins"),
    )
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    cors_allow_headers: List[str] = Field(default_factory=lambda: ["*"])

    production_origin: Optional[str] = Field(default=None, validation_alias=AliasChoices("PRODUCTION_ORIGIN"))

    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "log_level"))

    allow_open_registration: bool = Field(
        default=True,
        validation_alias=AliasChoices("ALLOW_OPEN_REGISTRATION", "allow_open_registration"),
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: object) -> List[str]:
        if v is None:
            return ["http://localhost:5173"]
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        if isinstance(v, str):
            s = v.strip()
            if s.startswith("["):
                import json

                try:
                    parsed = json.loads(s)
                    if isinstance(parsed, list):
                        return [str(x).strip() for x in parsed if str(x).strip()]
                except json.JSONDecodeError:
                    pass
            return [x.strip() for x in s.split(",") if x.strip()]
        return ["http://localhost:5173"]

    @property
    def allowed_origins(self) -> List[str]:
        origins = list(self.cors_origins)
        if self.production_origin:
            origins.append(self.production_origin)
        return origins

    @property
    def effective_debug(self) -> bool:
        return bool(self.debug or self.environment == "development")


settings = Settings()

logging.getLogger(__name__).debug("Config loaded: environment=%s", settings.environment)
