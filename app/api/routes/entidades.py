from fastapi import APIRouter, status

from app.api.dependencias import SessaoBanco, UsuarioAtual
from app.schemas.entidade import CriacaoEntidade, RespostaEntidade
from app.services.entidades import ServicoEntidade

roteador = APIRouter(prefix="/entidades", tags=["entidades"])


@roteador.post("", response_model=RespostaEntidade, status_code=status.HTTP_201_CREATED)
def criar_entidade(
    dados: CriacaoEntidade, usuario_atual: UsuarioAtual, sessao: SessaoBanco
) -> RespostaEntidade:
    return ServicoEntidade(sessao).criar(dados, usuario_atual)
