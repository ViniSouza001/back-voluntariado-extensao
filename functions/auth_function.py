from fastapi import HTTPException
from models.usuario import Usuario
from main import bcrypt_context

def autenticar_usuario(email: str, senha: str, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail não encontrado")
    elif not bcrypt_context.verify(senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    elif not usuario.confirmado:
        raise HTTPException(status_code=401, detail="Sua conta não foi confirmada ainda. Verifique a confirmação na sua caixa de e-mail")
    return usuario