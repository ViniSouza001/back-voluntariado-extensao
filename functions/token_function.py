from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

## dependencies
from main import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from dependencies import pegar_sessao

## libraries
from datetime import timedelta, datetime, timezone

## models
from models.usuario import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def criar_token(id_usuario, duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao, "tipo": "usuario"}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, algorithm=ALGORITHM)

    return jwt_codificado

def verificar_token_usuario(token: str = Depends(oauth2_scheme), session: Session = Depends(pegar_sessao)):
    try:
        dic_info = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id_usuario = int(dic_info.get("sub"))
        tipo = str(dic_info.get("tipo"))

        if id_usuario is None:
            raise HTTPException(401, "Token inválido")
        
        id_usuario = int(id_usuario)

    except JWTError:
        raise HTTPException(status_code=401, detail="Acesso negado, verifique a validade do token")
    
    if tipo != "usuario":
        raise HTTPException(status_code=401, detail="Você deve logar como usuário para acessar esta rota")

    usuario = session.query(Usuario).filter(Usuario.id == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=401, detail="Acesso inválido")
    return usuario