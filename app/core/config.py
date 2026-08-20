import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


# todas as variáveis de .env são pegas como strings pelo python
# pegar as variáveis booleanas de .env e retorna um boolean (True ou False)
def _as_boolean(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default

    normal_value = value.strip().lower()

    true_values = {"1", "on", "yes", "true", "verdadeiro", "sim", "ligado"}
    false_values = {"0", "off", "no", "false", "falso", "não", "desligado"}

    if normal_value in true_values:
        return True

    if normal_value in false_values:
            return False

    raise ValueError(f"Invalid boolean value: {normal_value}")

# pegar as listas de .env e retorna uma lista
def _as_list(value: str | None, default: list[str]) -> list[str]:
    if not value:
        return default

    return [item.strip() for item in value.split(",") if item.strip()]

def _get_url_database() -> str:
    env_url = os.getenv("URL_DATABASE")
    prefix_sqlite = "sqlite:///"

    # sem configuração, usa o SQLite padrão dentro do projeto
    if not env_url:
        return f"sqlite:///{(PROJECT_ROOT / 'data' / 'database.db').as_posix()}"

    # URL SQLite completa (sqlite:///C:\Users\User\Desktop\database)
    if env_url.startswith(prefix_sqlite):
        database_path = Path(env_url.removeprefix(prefix_sqlite))
        
        if not database_path.is_absolute():
            database_path = PROJECT_ROOT / database_path

            return f"{prefix_sqlite}{database_path.as_posix()}"

    # caminho puro, sem sqlite:/// (C:\Users\User\Desktop\database)
    database_path = Path(env_url)

    if database_path.is_absolute():
        return f"{prefix_sqlite}{database_path.as_posix()}"

    # Outras URLs (PostgreSQL ou MySQL)
    if "://" in env_url:
        return env_url

    # Caminho relativo puro (data/database.db)
    database_path = PROJECT_ROOT / database_path
    return f"{prefix_sqlite}{database_path.as_posix()}"


@dataclass(frozen=True)
class Configurations:
    application_name: str = field(
        default_factory=lambda: os.getenv("APPLICATION_NAME", "API da Plataforma de Voluntariado")
    )
    depuration: bool = field(default_factory=lambda: _as_boolean(os.getenv("DEPURATION")))
    prefix_api_v1: str = "/api/v1"
    
    url_database: str = field(default_factory = _get_url_database)
    secret_key: str = field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    algorithm: str = field(default_factory=lambda: os.getenv("ALGORITHM", "HS256"))

    minutes_expire_access_token: int = field(
        default_factory=lambda: int(os.getenv("MINUTES_EXPIRE_ACCESS_TOKEN", "30"))
    )
    minutes_expire_confirmation_email: int = field(
        default_factory=lambda: int(os.getenv("MINUTES_EXPIRE_CONFIRMATION_EMAIL", "20"))
    )
    minutes_resend_confirmation_email: int = field(
        default_factory=lambda: int(os.getenv("MINUTES_RESEND_CONFIRMATION_EMAIL", "5"))
    )

    origens_cors: list[str] = field(
        default_factory=lambda: _as_list(
            os.getenv("ORIGENS_CORS"),
            [
                "http://localhost:3000",
                "http://127.0.0.1:5500",
                "http://127.0.0.1:5173",
                "http://localhost:5173",
            ],    
        )
    )
    archives_directory: Path = PROJECT_ROOT / "uploads"

    enabled_email: bool = field(
        default_factory=lambda: _as_boolean(os.getenv("EMAIL_ENABLED"))
    )
    user_email: str = field(default_factory=lambda: os.getenv("USER_EMAIL", ""))
    password_email: str = field(default_factory=lambda: os.getenv("PASSWORD_EMAIL", ""))
    sender_email: str = field(default_factory=lambda: os.getenv("SENDER_EMAIL", ""))
    server_email: str = field(
        default_factory=lambda: os.getenv("SERVER_EMAIL", "smtp.gmail.com")
        )
    port_email: int = field(default_factory=lambda: int(os.getenv("PORT_EMAIL", "587")))
    url_frontend: str = field(default_factory=lambda: os.getenv("URL_FRONTEND", ""))

    def validate(self) -> None:
        if not self.secret_key:
            raise RuntimeError("SECRET_KEY must be configured on .env archive")
        if self.enabled_email and not all(
            (self.user_email, self.password_email, self.sender_email)
        ):
            raise RuntimeError(
                "'USER_EMAIL', 'PASSWORD_EMAIL' and 'SENDER_EMAIL' are required when 'EMAIL_ENABLED' = true"
                )

@lru_cache
def get_configurations() -> Configurations:
    configurations = Configurations()
    configurations.validate()

    return configurations
