from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.configuracao import obter_configuracoes
from app.db.sessao import obter_sessao
from app.models.usuario import Usuario
from app.repositories.usuarios import RepositorioUsuario

configuracoes = obter_configuracoes()
esquema_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{configuracoes.prefixo_api_v1}/autenticacao/entrar"
)
SessaoBanco = Annotated[Session, Depends(obter_sessao)]


def obter_usuario_atual(
    token: Annotated[str, Depends(esquema_oauth2)], sessao: SessaoBanco
) -> Usuario:
    erro_credenciais = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de acesso inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        conteudo_token = jwt.decode(
            token, configuracoes.chave_secreta, algorithms=[configuracoes.algoritmo]
        )
        identificador_usuario = conteudo_token.get("sub")
        if not identificador_usuario or conteudo_token.get("tipo") != "usuario":
            raise erro_credenciais
        id_usuario = int(identificador_usuario)
    except (JWTError, TypeError, ValueError) as erro:
        raise erro_credenciais from erro

    usuario = RepositorioUsuario.buscar_por_id(sessao, id_usuario)
    if not usuario:
        raise erro_credenciais
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(obter_usuario_atual)]
