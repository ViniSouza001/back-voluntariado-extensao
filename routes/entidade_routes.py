from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

## dependencies
from dependencies import pegar_sessao
from functions.token_function import verificar_token_usuario

## schemas
from schemas.entidade import EntidadeSchema
from schemas.usuario import UsuarioSchema
# from schemas.membro_entidade import Membro_entidadeSchema


## models
from models.usuario import Usuario

## functions
from functions.entity_functions import criar_entidade

entity_router = APIRouter(prefix="/entity", tags=["entity"])


@entity_router.post("/entidade")
def create_entity(entidade_schema: EntidadeSchema, usuario: Usuario = Depends(verificar_token_usuario), session: Session = Depends(pegar_sessao)):
    nova_entidade = criar_entidade(entidade_schema, usuario, session)
    if(nova_entidade):
        return {"mensagem": f"Entidade criada com sucesso. Você agora é um admin da entidade {nova_entidade.nome}"}