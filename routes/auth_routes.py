## dependencias
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

## arquivos
from dependencies import pegar_sessao
from services.email_service import enviar_confirmacao
from functions.user_function import criar_usuario, autenticar_usuario
from functions.token_function import criar_token

## python
import secrets
from datetime import datetime, timedelta

## functions
# from functions.auth_functions import...

## models
from models.usuario import Usuario
from models.confirmacao_email import ConfirmacaoEmail

## schemas
from schemas.usuario import UsuarioSchema, LoginSchema

## roteamento
auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/register")
async def criar_conta(usuario_schema: UsuarioSchema, session: Session = Depends(pegar_sessao)):
        
        senha_criptografada = criar_usuario(usuario_schema, session)

        novo_usuario = Usuario(
            usuario_schema.nome,
            usuario_schema.email,
            senha_criptografada,
            usuario_schema.data_nasc,
            usuario_schema.cidade,
            usuario_schema.uf,
            )
        session.add(novo_usuario)
        session.commit()

        session.refresh(novo_usuario)

        token = secrets.token_urlsafe(32)

        confirmacao = ConfirmacaoEmail(
            id_usuario = novo_usuario.id,
            token = token,
            criado_em= datetime.now(),
            expiracao= datetime.now() + timedelta(hours=1)
        )

        session.add(confirmacao)
        session.commit()

        await enviar_confirmacao(novo_usuario.email, token)

        return {"mensagem": "Usuário criado com sucesso! Confirme sua caixa de e-mail."}

@auth_router.post("/delete/{id_usuario}")
def deletar_usuario(id_usuario, session: Session = Depends(pegar_sessao)):
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Este usuário não existe")
    else:
        session.delete(usuario)
        session.commit()
        return {"Mensagem": "Usuário deletado com sucesso"}

@auth_router.get("/confirmar-email/{token}")
def confirmar_email(token: str, session: Session = Depends(pegar_sessao)):
    confirmacao = session.query(ConfirmacaoEmail).filter(ConfirmacaoEmail.token == token).first()

    if not confirmacao:
        raise HTTPException(status_code=404, detail="Token inválido")

    usuario = session.query(Usuario).filter(Usuario.id == confirmacao.id_usuario).first()

    usuario.confirmado = True
    session.delete(confirmacao)
    session.commit()

    return {"mensagem": "Usuário confirmado com sucesso! Você pode fazer login agora"}

@auth_router.post("/login")
def login(login_schema: LoginSchema, session: Session = Depends(pegar_sessao)):
    usuario = autenticar_usuario(login_schema.email, login_schema.senha, session)
    # se der erro ele já faz validação lá dentro
    access_token = criar_token(usuario.id)

    return {
        "user": usuario.nome,
        "access_token": access_token,
        "token_type": "bearer"
    }

