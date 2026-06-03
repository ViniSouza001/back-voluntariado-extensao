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

def alterar_dados(usuario, usuario_schema, session):
    dados = usuario_schema.model_dump(
        exclude_unset=True
    )

    alterou = False

    for campo, valor in dados.items():
        if getattr(usuario, campo) != valor:
            setattr(usuario, campo, valor)
            alterou = True
    
    if not alterou:
        return {"mensagem": "Nenhuma alteração detectada"}
    
    session.commit()
    session.refresh(usuario)

    return {"mensagem": "Dados atualizados com sucesso!", "usuario": usuario.nome}
    
def alterar_senha(dados, usuario, session):
    if not bcrypt_context.verify(dados.senha_atual, usuario.senha):
        raise HTTPException(401, "Senha atual incorreta")
    
    if bcrypt_context.verify(dados.nova_senha, usuario.senha):
        raise HTTPException(400, "A nova senha não pode ser igual a anterior")
    
    if (dados.nova_senha != dados.confirmar_nova_senha):
        raise HTTPException(400, "As novas senhas não coincidem")
    
    senha_bytes = dados.nova_senha.encode("utf-8")
    if len(senha_bytes) > MAX_BCRYPT_PASSWORD_BYTES:
        raise HTTPException(status_code=400, detail="A senha deve ter no máximo 72 bytes antes da criptografia. Use uma senha menor ou remova caracteres especiais.")

    senha_criptografada = bcrypt_context.hash(dados.nova_senha)
    usuario.senha = senha_criptografada
    
    session.commit()

    return {"mensagem": "Senha alterada com sucesso!"}