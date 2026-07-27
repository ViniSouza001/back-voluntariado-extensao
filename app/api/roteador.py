from fastapi import APIRouter

from app.api.routes import autenticacao, entidades, usuarios

roteador_api = APIRouter()
roteador_api.include_router(autenticacao.roteador)
roteador_api.include_router(usuarios.roteador)
roteador_api.include_router(entidades.roteador)
