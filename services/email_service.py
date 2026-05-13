from fastapi_mail import FastMail, MessageSchema
from config.email_config import conf

async def enviar_confirmacao(destinatario: str, token: str):
    link = f"http://localhost:8000/auth/confirmar-email/{token}"

    mensagem = MessageSchema(
        subject="Confirme sua conta",
        recipients=[destinatario],
        body=f"""
        Clique no link abaixo para confirmar sua conta

        {link}
        """,
        subtype="plain"
    )

    fm = FastMail(conf)
    
    await fm.send_message(mensagem)