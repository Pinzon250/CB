# app/core/config.py
from pydantic import Field, AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Esto lee el .env, no es sensible a mayusculas y minusculas y no falla por claves extra
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # --- DB ---
    DATABASE_URL: str = Field(
        ...,
        validation_alias=AliasChoices(
            "DATABASE_URL",
            "SQLALCHEMY_DATABASE_URI",
            "sqlalchemy_database",
            "SQLDATABASE_DATABASE",  
        ),
    )

    # --- Auth / JWT ---
    SECRET_KEY: str = Field(
        ...,
        validation_alias=AliasChoices(
            "SECRET_KEY",
            "AUTH_SECRET_KEY",
            "session_secret_key",
            "auth_secret_key",
        ),
    )
    ALGORITHM: str = Field(default="HS256", validation_alias=AliasChoices("ALGORITHM"))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        validation_alias=AliasChoices(
            "ACCESS_TOKEN_EXPIRE_MINUTES",
            "ACCESS_TOKEN_MINUTES",
            "TOKEN_MINUTES",
        ),
    )

    # --- Front/URLs ---
    FRONT_URL: str | None = Field(default=None, validation_alias=AliasChoices("FRONT_URL"))

    # --- CONFIGURACION DE EMAIL ---
    MAIL_USERNAME: str | None = Field(default=None, validation_alias=AliasChoices("MAIL_USERNAME", "email_origen"))
    MAIL_PASSWORD: str | None = Field(default=None, validation_alias=AliasChoices("MAIL_PASSWORD"))
    MAIL_FROM: str | None = Field(default=None, validation_alias=AliasChoices("MAIL_FROM", "email_origen"))
    MAIL_SERVER: str = Field(default="smtp.gmail.com", validation_alias=AliasChoices("MAIL_SERVER"))
    MAIL_PORT: int = Field(default=587, validation_alias=AliasChoices("MAIL_PORT"))
    MAIL_STARTTLS: bool = Field(default=True, validation_alias=AliasChoices("MAIL_STARTTLS"))
    MAIL_SSL_TLS: bool = Field(default=False, validation_alias=AliasChoices("MAIL_SSL_TLS"))
    USE_CREDENTIALS: bool = Field(default=True, validation_alias=AliasChoices("USE_CREDENTIALS"))

    # --- Google OAuth ---
    GOOGLE_CLIENT_ID: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_ID", "google_client_id"))
    GOOGLE_CLIENT_SECRET: str | None = Field(default=None, validation_alias=AliasChoices("GOOGLE_CLIENT_SECRET", "google_client_secret"))

settings = Settings()
