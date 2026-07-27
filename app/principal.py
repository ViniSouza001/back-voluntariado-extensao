from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.roteador import roteador_api
from app.core.configuracao import obter_configuracoes
from app.core.excecoes import ErroAplicacao


def criar_aplicacao() -> FastAPI:
    configuracoes = obter_configuracoes()
    aplicacao_fastapi = FastAPI(title=configuracoes.nome_aplicacao, debug=configuracoes.depuracao)

    aplicacao_fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=configuracoes.origens_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @aplicacao_fastapi.exception_handler(ErroAplicacao)
    async def tratar_erro_aplicacao(_requisicao: Request, erro: ErroAplicacao) -> JSONResponse:
        return JSONResponse(status_code=erro.codigo_status, content={"detalhe": erro.detalhe})

    @aplicacao_fastapi.get("/saude", tags=["sistema"])
    def verificar_saude() -> dict[str, str]:
        return {"estado": "saudável"}

    aplicacao_fastapi.include_router(roteador_api, prefix=configuracoes.prefixo_api_v1)
    aplicacao_fastapi.mount(
        "/arquivos",
        StaticFiles(directory=configuracoes.diretorio_arquivos),
        name="arquivos",
    )
    return aplicacao_fastapi


aplicacao = criar_aplicacao()
