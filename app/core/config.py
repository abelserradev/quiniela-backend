from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # POSTGRES_*, DB_PORT son para Docker, no para Settings
    )

    app_name: str = "Quiniela API"
    debug: bool = False
    environment: Literal["development", "production"] = "development"

    database_url: str = Field(
        default="postgresql://user:password@localhost:5432/quiniela",
        description="URL de la base de datos",
    )

    jwt_secret_key: str = Field(
        default="cambiar-en-produccion-usar-secretos-seguros-minimo-32-chars",
        min_length=32,
    )

    @field_validator("environment", mode="before")
    @classmethod
    def env_si_vacio(cls, v: str) -> str:
        if v == "" or v is None:
            return "development"
        return v

    @field_validator("jwt_secret_key", mode="before")
    @classmethod
    def jwt_si_vacio(cls, v: str) -> str:
        if v == "" or v is None:
            return "cambiar-en-produccion-usar-secretos-seguros-minimo-32-chars"
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def cors_si_vacio(cls, v: str) -> str:
        if v == "" or v is None:
            return "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"
        return v

    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60 * 24 * 7  # 1 semana

    api_key: str | None = Field(default=None)
    api_key_hash: str | None = Field(default=None)

    api_football_key: str | None = None
    api_football_base_url: str = "https://v3.football.api-sports.io"

    # Cookie de sesión: HttpOnly evita robo por XSS
    auth_cookie_name: str = "access_token"
    auth_cookie_secure: bool = False  # True en producción con HTTPS
    auth_cookie_samesite: str = "lax"

    # CORS: orígenes permitidos separados por coma (ej. http://localhost:3000,http://127.0.0.1:3000)
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001,http://127.0.0.1:3001"


@lru_cache
def get_settings() -> Settings:
    return Settings()