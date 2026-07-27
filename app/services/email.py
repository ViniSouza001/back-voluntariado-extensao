import logging

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.configuracao import Configuracoes, obter_configuracoes

registrador = logging.getLogger(__name__)


class ServicoEmail:
    def __init__(self, configuracoes: Configuracoes | None = None):
        self.configuracoes = configuracoes or obter_configuracoes()

    async def enviar_confirmacao(self, destinatario: str, token: str) -> bool:
        if not self.configuracoes.email_habilitado:
            registrador.warning(
                "O e-mail de confirmação não foi enviado porque o serviço está desativado"
            )
            return False

        url_base = self.configuracoes.url_frontend.rstrip("/")
        if url_base:
            url_confirmacao = f"{url_base}/confirmar-email?token={token}"
        else:
            url_confirmacao = (
                f"http://localhost:8000{self.configuracoes.prefixo_api_v1}"
                f"/autenticacao/confirmar-email/{token}"
            )

        configuracao = ConnectionConfig(
            MAIL_USERNAME=self.configuracoes.usuario_email,
            MAIL_PASSWORD=self.configuracoes.senha_email,
            MAIL_FROM=self.configuracoes.remetente_email,
            MAIL_PORT=self.configuracoes.porta_email,
            MAIL_SERVER=self.configuracoes.servidor_email,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        mensagem = MessageSchema(
            subject="Confirme sua conta",
            recipients=[destinatario],
            body=(f"Use o link abaixo para confirmar sua conta:\n\n{url_confirmacao}\n"),
            subtype="plain",
        )

        try:
            await FastMail(configuracao).send_message(mensagem)
        except Exception:
            registrador.exception("Falha ao enviar o e-mail de confirmação")
            return False
        return True
