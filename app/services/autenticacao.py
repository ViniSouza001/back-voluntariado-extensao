import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.configuracao import obter_configuracoes
from app.core.excecoes import (
    ErroAutenticacao,
    ErroConflito,
    ErroNaoEncontrado,
    ErroValidacao,
)
from app.core.seguranca import (
    gerar_hash_senha,
    gerar_hash_token_confirmacao,
    verificar_senha,
)
from app.models.confirmacao_email import ConfirmacaoEmail
from app.models.usuario import Usuario
from app.repositories.confirmacoes_email import RepositorioConfirmacaoEmail
from app.repositories.usuarios import RepositorioUsuario
from app.schemas.autenticacao import CadastroUsuario
from app.services.email import ServicoEmail
from app.utils.cpf import cpf_valido, normalizar_cpf


class ServicoAutenticacao:
    def __init__(self, sessao: Session, servico_email: ServicoEmail | None = None):
        self.sessao = sessao
        self.servico_email = servico_email or ServicoEmail()
        self.configuracoes = obter_configuracoes()

    async def cadastrar(self, dados: CadastroUsuario) -> tuple[Usuario, bool]:
        cpf = normalizar_cpf(dados.cpf)
        if not cpf_valido(cpf):
            raise ErroValidacao("CPF inválido")
        if RepositorioUsuario.buscar_por_email(self.sessao, str(dados.email)):
            raise ErroConflito("Já existe uma conta com este e-mail")
        if RepositorioUsuario.buscar_por_cpf(self.sessao, cpf):
            raise ErroConflito("Já existe uma conta com este CPF")

        try:
            senha_hash = gerar_hash_senha(dados.senha)
        except ValueError as erro:
            raise ErroValidacao(str(erro)) from erro

        usuario = Usuario(
            nome=dados.nome.strip(),
            cpf=cpf,
            email=str(dados.email).lower(),
            senha_hash=senha_hash,
            data_nascimento=dados.data_nascimento,
            cidade=dados.cidade.strip(),
            uf=dados.uf.upper(),
        )
        token_original = secrets.token_urlsafe(32)
        agora = datetime.now(UTC)

        try:
            RepositorioUsuario.adicionar(self.sessao, usuario)
            self.sessao.flush()
            self.sessao.add(
                ConfirmacaoEmail(
                    id_usuario=usuario.id,
                    hash_token=gerar_hash_token_confirmacao(token_original),
                    criado_em=agora,
                    expira_em=agora
                    + timedelta(minutes=self.configuracoes.minutos_expiracao_confirmacao_email),
                )
            )
            self.sessao.commit()
            self.sessao.refresh(usuario)
        except IntegrityError as erro:
            self.sessao.rollback()
            raise ErroConflito("O e-mail ou CPF já está cadastrado") from erro
        except Exception:
            self.sessao.rollback()
            raise

        email_enviado = await self.servico_email.enviar_confirmacao(usuario.email, token_original)
        return usuario, email_enviado

    def autenticar(self, email: str, senha: str) -> Usuario:
        usuario = RepositorioUsuario.buscar_por_email(self.sessao, email)
        if not usuario or not verificar_senha(senha, usuario.senha_hash):
            raise ErroAutenticacao("E-mail ou senha inválidos")
        if not usuario.email_confirmado:
            raise ErroAutenticacao("Confirme seu e-mail antes de entrar")
        return usuario

    def confirmar_email(self, token: str) -> None:
        confirmacao = RepositorioConfirmacaoEmail.buscar_por_hash_token(
            self.sessao, gerar_hash_token_confirmacao(token)
        )
        if not confirmacao:
            raise ErroNaoEncontrado("Token de confirmação inválido")

        expira_em = confirmacao.expira_em
        if expira_em.tzinfo is None:
            expira_em = expira_em.replace(tzinfo=UTC)
        if expira_em < datetime.now(UTC):
            self.sessao.delete(confirmacao)
            self.sessao.commit()
            raise ErroValidacao("O token de confirmação expirou")

        usuario = RepositorioUsuario.buscar_por_id(self.sessao, confirmacao.id_usuario)
        if not usuario:
            self.sessao.delete(confirmacao)
            self.sessao.commit()
            raise ErroNaoEncontrado("O usuário não existe mais")

        usuario.email_confirmado = True
        RepositorioConfirmacaoEmail.excluir_do_usuario(self.sessao, usuario.id)
        self.sessao.commit()

    async def reenviar_confirmacao(self, email: str) -> bool:
        usuario = RepositorioUsuario.buscar_por_email(self.sessao, email)
        if not usuario or usuario.email_confirmado:
            return False

        token_original = secrets.token_urlsafe(32)
        agora = datetime.now(UTC)
        RepositorioConfirmacaoEmail.excluir_do_usuario(self.sessao, usuario.id)
        self.sessao.add(
            ConfirmacaoEmail(
                id_usuario=usuario.id,
                hash_token=gerar_hash_token_confirmacao(token_original),
                criado_em=agora,
                expira_em=agora
                + timedelta(minutes=self.configuracoes.minutos_expiracao_confirmacao_email),
            )
        )
        self.sessao.commit()
        return await self.servico_email.enviar_confirmacao(usuario.email, token_original)
