import logging
from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from jinja2 import Environment, FileSystemLoader

from app.core.config import Configurations, get_configurations

register = logging.getLogger(__name__)
TEMPLATES_DIRECTORY = Path(__file__).resolve().parents[1] / "templates"


class EmailService:
    def __init__(self, configurations: Configurations | None = None):
        self.configurations = configurations or get_configurations()

    async def send_confirmation(self, recipient: str, token: str) -> bool:
        if not self.configurations.enabled_email:
            register.warning(
                "A confirmação de e-mail não foi enviada porque o serviço está desabilitado"
            )
            return False
        url_base = self.configurations.url_frontend.rstrip("/")
        if url_base:
            url_confirmation = f"{url_base}/confirmacao?token={token}"
        else:
            url_confirmation = (
                f"http://localhost:8000{self.configurations.prefix_api_v1}"
                f"/auth/confirm-email/{token}"
            )

        configuration = ConnectionConfig(
            MAIL_USERNAME=self.configurations.user_email,
            MAIL_PASSWORD=self.configurations.password_email,
            MAIL_FROM=self.configurations.sender_email,
            MAIL_PORT=self.configurations.port_email,
            MAIL_SERVER=self.configurations.server_email,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        message = MessageSchema(
            subject="Confirme sua conta",
            recipients=[recipient],
            body=Environment(loader=FileSystemLoader(TEMPLATES_DIRECTORY)).get_template(
                "confirm-login.html"
            ).render(url_confirmation=url_confirmation),
            subtype="html",
        )

        try:
            await FastMail(configuration).send_message(message)
        except Exception:
            register.exception("Failed to send confirmation e-mail")
            return False
            
        return True