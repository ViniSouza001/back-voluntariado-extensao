import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


def _as_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _as_list(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default
    return [item.strip() for item in value.split(",") if item.strip()]


def _database_url() -> str:
    configured_url = os.getenv("DATABASE_URL")
    if not configured_url:
        return f"sqlite:///{(PROJECT_ROOT / 'database' / 'database.db').as_posix()}"
    sqlite_prefix = "sqlite:///"
    if configured_url.startswith(sqlite_prefix):
        database_path = Path(configured_url.removeprefix(sqlite_prefix))
        if not database_path.is_absolute():
            return f"{sqlite_prefix}{(PROJECT_ROOT / database_path).as_posix()}"
    return configured_url


@dataclass(frozen=True)
class Settings:
    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Volunteer Platform API"))
    debug: bool = field(default_factory=lambda: _as_bool(os.getenv("DEBUG")))
    api_v1_prefix: str = "/api/v1"

    database_url: str = field(default_factory=_database_url)
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    algorithm: str = field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))
    access_token_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    )
    email_confirmation_expire_minutes: int = field(
        default_factory=lambda: int(os.getenv("EMAIL_CONFIRMATION_EXPIRE_MINUTES", "60"))
    )

    cors_origins: list[str] = field(
        default_factory=lambda: _as_list(
            os.getenv("CORS_ORIGINS"),
            [
                "http://localhost:3000",
                "http://127.0.0.1:5500",
                "http://127.0.0.1:5173",
                "http://localhost:5173",
            ],
        )
    )
    uploads_directory: Path = PROJECT_ROOT / "uploads"

    email_enabled: bool = field(default_factory=lambda: _as_bool(os.getenv("EMAIL_ENABLED")))
    mail_username: str = field(default_factory=lambda: os.getenv("MAIL_USERNAME", ""))
    mail_password: str = field(default_factory=lambda: os.getenv("MAIL_PASSWORD", ""))
    mail_from: str = field(default_factory=lambda: os.getenv("MAIL_FROM", ""))
    mail_server: str = field(default_factory=lambda: os.getenv("MAIL_SERVER", "smtp.gmail.com"))
    mail_port: int = field(default_factory=lambda: int(os.getenv("MAIL_PORT", "587")))
    frontend_url: str = field(default_factory=lambda: os.getenv("FRONTEND_URL", ""))

    def validate(self) -> None:
        if not self.secret_key:
            raise RuntimeError("SECRET_KEY must be configured in the .env file")
        if self.email_enabled and not all((self.mail_username, self.mail_password, self.mail_from)):
            raise RuntimeError(
                "MAIL_USERNAME, MAIL_PASSWORD and MAIL_FROM are required when EMAIL_ENABLED=true"
            )


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.validate()
    return settings
