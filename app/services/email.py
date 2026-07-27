import logging

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, settings: Settings | None = None):
        self.settings = settings or get_settings()

    async def send_confirmation(self, recipient: str, token: str) -> bool:
        if not self.settings.email_enabled:
            logger.warning("Confirmation email was not sent because email delivery is disabled")
            return False

        base_url = self.settings.frontend_url.rstrip("/")
        if base_url:
            confirmation_url = f"{base_url}/confirm-email?token={token}"
        else:
            confirmation_url = (
                f"http://localhost:8000{self.settings.api_v1_prefix}/auth/confirm-email/{token}"
            )

        configuration = ConnectionConfig(
            MAIL_USERNAME=self.settings.mail_username,
            MAIL_PASSWORD=self.settings.mail_password,
            MAIL_FROM=self.settings.mail_from,
            MAIL_PORT=self.settings.mail_port,
            MAIL_SERVER=self.settings.mail_server,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        message = MessageSchema(
            subject="Confirm your account",
            recipients=[recipient],
            body=(f"Use the link below to confirm your account:\n\n{confirmation_url}\n"),
            subtype="plain",
        )

        try:
            await FastMail(configuration).send_message(message)
        except Exception:
            logger.exception("Failed to send a confirmation email")
            return False
        return True
