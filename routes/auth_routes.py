from fastapi import APIRouter, Depends, HTTPException
from schemas.usuario import UsuarioSchema
from dependencies import get_session
from main import bcrypt_context, ALGORITHM, SECRET_KEY
from sqlalchemy.orm import Session
from models.usuario import Usuario

# roteamento
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.email == usuario_schema.email).first()
    print(usuario)
    if usuario:
        raise HTTPException(status_code=400, detail="E-mail do usuário já cadastrado")
    else:
        senha_criptografada = bcrypt_context.hash(usuario_schema.senha)
        novo_usuario = Usuario(
            usuario_schema.nome,
            usuario_schema.email,
            senha_criptografada,
            usuario_schema.data_nasc,
            usuario_schema.cidade,
            usuario_schema.uf,
            usuario_schema.confirmado,
            usuario_schema.admin
            )
        session.add(novo_usuario)
        session.commit()
        return {"Mensagem": f"Usuario cadastrado com sucesso com e-mail {usuario_schema.email}"}

@auth_router.post("/delete/{id_usuario}")
async def deletar_usuario(id_usuario, session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Este usuário não existe")
    else:
        session.delete(usuario)
        session.commit()
        return {"Mensagem": "Usuário deletado com sucesso"}