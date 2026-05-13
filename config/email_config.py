from fastapi_mail import ConnectionConfig

conf = ConnectionConfig(
    MAIL_USERNAME="vvsouza.dev@gmail.com",
    MAIL_PASSWORD="ipoe xjsh ujpr twkh",
    MAIL_FROM="vvsouza.dev@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True
)