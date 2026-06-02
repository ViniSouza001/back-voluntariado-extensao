from fastapi import HTTPException
from models.usuario import Usuario
from main import bcrypt_context

MAX_BCRYPT_PASSWORD_BYTES = 72

def criar_usuario(usuario_schema, session):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    if usuario:
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado")

    senha = usuario_schema.senha
    senha_bytes = senha.encode("utf-8")
    if len(senha_bytes) > MAX_BCRYPT_PASSWORD_BYTES:
        raise HTTPException(
            status_code=400,
            detail="A senha deve ter no máximo 72 bytes antes da criptografia. Use uma senha menor ou remova caracteres especiais."
        )

    senha_criptografada = bcrypt_context.hash(senha)
    return senha_criptografada
    
def autenticar_usuario(email: str, senha: str, session):
    usuario = session.query(Usuario).filter(Usuario.email == email).first()

    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail não encontrado")
    elif not bcrypt_context.verify(senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Senha incorreta")
    elif not usuario.confirmado:
        raise HTTPException(status_code=401, detail="Sua conta não foi confirmada ainda. Verifique a confirmação na sua caixa de e-mail")
    return usuario