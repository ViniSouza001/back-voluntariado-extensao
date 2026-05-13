from jose import jwt
from main import ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM
from datetime import timedelta, datetime, timezone
from models.usuario import Usuario
from fastapi import Depends

def criar_token(id_usuario, duracao_token = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    data_expiracao = datetime.now(timezone.utc) + duracao_token
    dic_info = {"sub": str(id_usuario), "exp": data_expiracao}
    jwt_codificado = jwt.encode(dic_info, SECRET_KEY, ALGORITHM)

    return jwt_codificado

# def recarregar_token(usuario: Usuario = Depends(verificar_token)):
    # return 0