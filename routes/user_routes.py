## dependências
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from schemas.usuario import UsuarioUpdateSchema, AlterarSenhaSchema

## python sys
import os
import shutil

## demais arquivos
from dependencies import pegar_sessao

## models
from models.usuario import Usuario

## schemas
from schemas.usuario import UsuarioDataResponseSchema

## functions
from functions.user_function import alterar_dados, alterar_senha
from functions.token_function import verificar_token_usuario

## roteamento
user_router = APIRouter(prefix="/user", tags=["user"])

### consulta e atualização de dados
@user_router.get("/me", response_model=UsuarioDataResponseSchema)
def consultar_dados(usuario: Usuario = Depends(verificar_token_usuario)):
    return usuario

@user_router.patch("/me/{token}")
def atualizar_dados(usuario_schema: UsuarioUpdateSchema, usuario: Usuario = Depends(verificar_token_usuario), session: Session = Depends(pegar_sessao)):

    return alterar_dados(usuario, usuario_schema, session)

## atualização de senhas
@user_router.patch("/me/senha/{token}")
def atualizar_senha(dados: AlterarSenhaSchema, usuario: Usuario = Depends(verificar_token_usuario), session: Session = Depends(pegar_sessao)):
    return alterar_senha(dados, usuario, session)

@user_router.post("/me/foto")
def atualizar_foto_perfil(foto: UploadFile = File(...),
                          usuario: Usuario = Depends(verificar_token_usuario),
                          session: Session = Depends(pegar_sessao)):
    pasta = "uploads/fotos_perfil"
    os.makedirs(pasta, exist_ok=True)

    extensao = foto.filename.split(".")[-1]
    nome_arquivo = f"usuario_{usuario.id}.{extensao}"
    caminho_arquivo = f"{pasta}/{nome_arquivo}"

    with open(caminho_arquivo, "wb") as buffer:
        shutil.copyfileobj(foto.file, buffer)

        usuario.foto_perfil = f"/{caminho_arquivo}"
        
        session.commit()
        session.refresh(usuario)

        return {
            "mensagem": "Foto de perfil atualizada com sucesso!",
            "foto_perfil": usuario.foto_perfil
            }