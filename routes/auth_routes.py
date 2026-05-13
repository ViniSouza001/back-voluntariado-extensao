from fastapi import APIRouter, Depends, HTTPException
from schemas.usuario import UsuarioSchema
from services.email_service import enviar_confirmacao
from dependencies import get_session
import secrets
from datetime import datetime, timedelta
from main import bcrypt_context, ALGORITHM, SECRET_KEY
from sqlalchemy.orm import Session
from models.usuario import Usuario
from models.confirmacao_email import ConfirmacaoEmail

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
            usuario_schema.admin
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
async def deletar_usuario(id_usuario, session: Session = Depends(get_session)):
    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Este usuário não existe")
    else:
        session.delete(usuario)
        session.commit()
        return {"Mensagem": "Usuário deletado com sucesso"}
    
@auth_router.get("/confirmar-email/{token}")
async def confirmar_email(token: str, session: Session = Depends(get_session)):
    confirmacao = session.query(ConfirmacaoEmail).filter(ConfirmacaoEmail.token == token).first()

    if not confirmacao:
        raise HTTPException(status_code=404, detail="Token inválido")
    
    usuario = session.query(Usuario).filter(Usuario.id == confirmacao.id_usuario).first()

    usuario.confirmado = True
    session.delete(confirmacao)
    session.commit()

    return {"mensagem": "Usuário confirmado com sucesso! Você pode fazer login agora"}