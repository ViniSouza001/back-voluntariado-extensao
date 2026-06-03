from fastapi_mail import FastMail, MessageSchema
from config.email_config import conf

async def enviar_confirmacao(destinatario: str, token: str):
    ## Para testar com front-end
    # link = f"http://127.0.0.1:5500/pages/confirmar.html?token={token}"
    ## Testar somente com back-end
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