import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

RAIZ_PROJETO = Path(__file__).resolve().parents[2]
load_dotenv(RAIZ_PROJETO / ".env")


def _como_booleano(valor: str | None, padrao: bool = False) -> bool:
    if valor is None:
        return padrao
    return valor.strip().lower() in {"1", "true", "sim", "yes", "on"}


def _como_lista(valor: str | None, padrao: list[str]) -> list[str]:
    if not valor:
        return padrao
    return [origem.strip() for origem in valor.split(",") if origem.strip()]


def _obter_url_banco() -> str:
    url_configurada = os.getenv("URL_BANCO")
    if not url_configurada:
        return f"sqlite:///{(RAIZ_PROJETO / 'data' / 'banco.db').as_posix()}"
    prefixo_sqlite = "sqlite:///"
    if url_configurada.startswith(prefixo_sqlite):
        caminho_banco = Path(url_configurada.removeprefix(prefixo_sqlite))
        if not caminho_banco.is_absolute():
            return f"{prefixo_sqlite}{(RAIZ_PROJETO / caminho_banco).as_posix()}"
    return url_configurada


@dataclass(frozen=True)
class Configuracoes:
    nome_aplicacao: str = field(
        default_factory=lambda: os.getenv("NOME_APLICACAO", "API da Plataforma de Voluntariado")
    )
    depuracao: bool = field(default_factory=lambda: _como_booleano(os.getenv("DEPURACAO")))
    prefixo_api_v1: str = "/api/v1"

    url_banco: str = field(default_factory=_obter_url_banco)
    chave_secreta: str = field(default_factory=lambda: os.getenv("CHAVE_SECRETA", ""))
    algoritmo: str = field(default_factory=lambda: os.getenv("ALGORITMO", "HS256"))
    minutos_expiracao_token_acesso: int = field(
        default_factory=lambda: int(os.getenv("MINUTOS_EXPIRACAO_TOKEN_ACESSO", "30"))
    )
    minutos_expiracao_confirmacao_email: int = field(
        default_factory=lambda: int(os.getenv("MINUTOS_EXPIRACAO_CONFIRMACAO_EMAIL", "60"))
    )

    origens_cors: list[str] = field(
        default_factory=lambda: _como_lista(
            os.getenv("ORIGENS_CORS"),
            [
                "http://localhost:3000",
                "http://127.0.0.1:5500",
                "http://127.0.0.1:5173",
                "http://localhost:5173",
            ],
        )
    )
    diretorio_arquivos: Path = RAIZ_PROJETO / "uploads"

    email_habilitado: bool = field(
        default_factory=lambda: _como_booleano(os.getenv("EMAIL_HABILITADO"))
    )
    usuario_email: str = field(default_factory=lambda: os.getenv("USUARIO_EMAIL", ""))
    senha_email: str = field(default_factory=lambda: os.getenv("SENHA_EMAIL", ""))
    remetente_email: str = field(default_factory=lambda: os.getenv("REMETENTE_EMAIL", ""))
    servidor_email: str = field(
        default_factory=lambda: os.getenv("SERVIDOR_EMAIL", "smtp.gmail.com")
    )
    porta_email: int = field(default_factory=lambda: int(os.getenv("PORTA_EMAIL", "587")))
    url_frontend: str = field(default_factory=lambda: os.getenv("URL_FRONTEND", ""))

    def validar(self) -> None:
        if not self.chave_secreta:
            raise RuntimeError("CHAVE_SECRETA deve ser configurada no arquivo .env")
        if self.email_habilitado and not all(
            (self.usuario_email, self.senha_email, self.remetente_email)
        ):
            raise RuntimeError(
                "USUARIO_EMAIL, SENHA_EMAIL e REMETENTE_EMAIL são obrigatórios quando "
                "EMAIL_HABILITADO=true"
            )


@lru_cache
def obter_configuracoes() -> Configuracoes:
    configuracoes = Configuracoes()
    configuracoes.validar()
    return configuracoes
