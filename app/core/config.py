from pathlib import Path
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict
from dotenv import load_dotenv, find_dotenv

# Localiza el .env
_env_file = find_dotenv(filename=".env", usecwd=True)
if not _env_file:
    candidate = (Path(__file__).resolve().parent / ".env")
    if candidate.exists():
        _env_file = str(candidate)

# Si no lo encuentra mostrar mensaje de error
if not _env_file:
    raise RuntimeError(
        "No se encontró el archivo .env."
    )

load_dotenv(_env_file, override=False)

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
    )

    # --- DB ---
    DATABASE_URL: str = Field(
        ...,
        validation_alias=AliasChoices(
            "DATABASE_URL",
            "SQLALCHEMY_DATABASE_URL",
            "SQLALCHEMY_DATABASE_RW",
            "SQLALCHEMY_DATABASE_LH",
        ),
    )

    # --- Auth / JWT ---
    SECRET_KEY: str = Field(
        ...,
        validation_alias=AliasChoices(
            "AUTH_SECRET_KEY",
            "SECRET_KEY",
            "SESSION_SECRET_KEY",
            "session_secret_key",
            "auth_secret_key",
        ),
    )
    ALGORITHM: str = Field(default="HS256", validation_alias=AliasChoices("ALGORITHM"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_EXPIRE_MINUTES", "ACCESS_TOKEN_MINUTES", "TOKEN_MINUTES",
        ),
    )

    # --- Front / URLs ---
    FRONT_URL: str | None = Field(default=None, validation_alias=AliasChoices("FRONT_URL"))

    # --- Email ---
    MAIL_USERNAME: str | None = Field(default=None, validation_alias=AliasChoices("MAIL_USERNAME", "EMAIL_ORIGEN", "email_origen"))
    MAIL_PASSWORD: str | None = Field(default=None, validation_alias=AliasChoices("MAIL_PASSWORD"))
    MAIL_FROM: str | None = Field(default=None, validation_alias=AliasChoices("MAIL_FROM", "EMAIL_ORIGEN", "email_origen"))
    MAIL_SERVER: str = Field(default="smtp.gmail.com", validation_alias=AliasChoices("MAIL_SERVER"))
    MAIL_PORT: int = Field(default=587, validation_alias=AliasChoices("MAIL_PORT"))
    MAIL_STARTTLS: bool = Field(default=True, validation_alias=AliasChoices("MAIL_STARTTLS"))
    MAIL_SSL_TLS: bool = Field(default=False, validation_alias=AliasChoices("MAIL_SSL_TLS"))
    USE_CREDENTIALS: bool = Field(default=True, validation_alias=AliasChoices("USE_CREDENTIALS"))

    # --- Google OAuth ---
    GOOGLE_CLIENT_ID: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "google_client_id"))
    GOOGLE_CLIENT_SECRET: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "google_client_secret"))

settings = Settings()
