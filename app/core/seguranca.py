import hashlib
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app.core.configuracao import obter_configuracoes

MAXIMO_BYTES_SENHA = 72


def gerar_hash_senha(senha: str) -> str:
    senha_em_bytes = senha.encode("utf-8")
    if len(senha_em_bytes) > MAXIMO_BYTES_SENHA:
        raise ValueError("A senha não pode ultrapassar 72 bytes")
    return bcrypt.hashpw(senha_em_bytes, bcrypt.gensalt()).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    senha_em_bytes = senha.encode("utf-8")
    if len(senha_em_bytes) > MAXIMO_BYTES_SENHA:
        return False
    try:
        return bcrypt.checkpw(senha_em_bytes, senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_token_acesso(id_usuario: int, duracao_personalizada: timedelta | None = None) -> str:
    configuracoes = obter_configuracoes()
    expira_em = datetime.now(UTC) + (
        duracao_personalizada or timedelta(minutes=configuracoes.minutos_expiracao_token_acesso)
    )
    conteudo_token = {"sub": str(id_usuario), "exp": expira_em, "tipo": "usuario"}
    return jwt.encode(
        conteudo_token,
        configuracoes.chave_secreta,
        algorithm=configuracoes.algoritmo,
    )


def gerar_hash_token_confirmacao(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
