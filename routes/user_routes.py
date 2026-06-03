## dependências
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioUpdateSchema, AlterarSenhaSchema

## demais arquivos
from dependencies import pegar_sessao

## models
from models.usuario import Usuario

## schemas
from schemas.usuario import UsuarioDataResponseSchema

## functions
from functions.user_function import alterar_dados, alterar_senha
from functions.token_function import verificar_token

## roteamento
user_router = APIRouter(prefix="/user", tags=["user"])

### consulta e atualização de dados
@user_router.get("/me/{token}", response_model=UsuarioDataResponseSchema)
def consultar_dados(usuario: Usuario = Depends(verificar_token)):
    return usuario

@user_router.patch("/me/{token}")
def atualizar_dados(usuario_schema: UsuarioUpdateSchema, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):

    return alterar_dados(usuario, usuario_schema, session)

## atualização de senhas
@user_router.patch("/me/senha/{token}")
def atualizar_senha(dados: AlterarSenhaSchema, usuario: Usuario = Depends(verificar_token), session: Session = Depends(pegar_sessao)):
    return alterar_senha(dados, usuario, session)
