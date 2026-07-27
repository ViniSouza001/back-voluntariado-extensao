from fastapi import APIRouter, Response, status

from app.api.dependencias import SessaoBanco, UsuarioAtual
from app.schemas.comum import RespostaMensagem
from app.schemas.usuario import AlteracaoSenha, AtualizacaoUsuario, RespostaUsuario
from app.services.usuarios import ServicoUsuario

roteador = APIRouter(prefix="/usuarios", tags=["usuários"])


@roteador.get("/eu", response_model=RespostaUsuario)
def consultar_perfil(usuario_atual: UsuarioAtual) -> RespostaUsuario:
    return usuario_atual


@roteador.patch("/eu", response_model=RespostaUsuario)
def atualizar_perfil(
    dados: AtualizacaoUsuario, usuario_atual: UsuarioAtual, sessao: SessaoBanco
) -> RespostaUsuario:
    return ServicoUsuario(sessao).atualizar(usuario_atual, dados)


@roteador.patch("/eu/senha", response_model=RespostaMensagem)
def alterar_senha(
    dados: AlteracaoSenha, usuario_atual: UsuarioAtual, sessao: SessaoBanco
) -> RespostaMensagem:
    ServicoUsuario(sessao).alterar_senha(usuario_atual, dados)
    return RespostaMensagem(mensagem="Senha alterada com sucesso")


@roteador.delete("/eu", status_code=status.HTTP_204_NO_CONTENT)
def excluir_conta(usuario_atual: UsuarioAtual, sessao: SessaoBanco) -> Response:
    ServicoUsuario(sessao).excluir(usuario_atual)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
