from fastapi import APIRouter, status

from app.api.dependencias import SessaoBanco
from app.core.seguranca import criar_token_acesso
from app.schemas.autenticacao import (
    CadastroUsuario,
    RespostaCadastro,
    RespostaToken,
    SolicitacaoLogin,
    SolicitacaoReenvioConfirmacao,
)
from app.schemas.comum import RespostaMensagem
from app.services.autenticacao import ServicoAutenticacao

roteador = APIRouter(prefix="/autenticacao", tags=["autenticação"])


@roteador.post("/cadastro", response_model=RespostaCadastro, status_code=status.HTTP_201_CREATED)
async def cadastrar(dados: CadastroUsuario, sessao: SessaoBanco) -> RespostaCadastro:
    _usuario, email_enviado = await ServicoAutenticacao(sessao).cadastrar(dados)
    return RespostaCadastro(
        mensagem="Conta criada. Confirme seu e-mail antes de entrar.",
        email_confirmacao_enviado=email_enviado,
    )


@roteador.post("/entrar", response_model=RespostaToken)
def entrar(dados: SolicitacaoLogin, sessao: SessaoBanco) -> RespostaToken:
    usuario = ServicoAutenticacao(sessao).autenticar(str(dados.email), dados.senha)
    return RespostaToken(usuario=usuario.nome, token_acesso=criar_token_acesso(usuario.id))


@roteador.get("/confirmar-email/{token}", response_model=RespostaMensagem)
def confirmar_email(token: str, sessao: SessaoBanco) -> RespostaMensagem:
    ServicoAutenticacao(sessao).confirmar_email(token)
    return RespostaMensagem(mensagem="E-mail confirmado. Agora você pode entrar.")


@roteador.post("/reenviar-confirmacao", response_model=RespostaMensagem)
async def reenviar_confirmacao(
    dados: SolicitacaoReenvioConfirmacao, sessao: SessaoBanco
) -> RespostaMensagem:
    await ServicoAutenticacao(sessao).reenviar_confirmacao(str(dados.email))
    return RespostaMensagem(
        mensagem="Se existir uma conta não confirmada, um novo e-mail será enviado."
    )
