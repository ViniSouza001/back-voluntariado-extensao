from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.router import router_api
from app.core.exceptions import ApplicationError
from app.core.config import get_configurations

def create_application() -> FastAPI:
    configurations = get_configurations()
    application_fastapi = FastAPI(title=configurations.application_name, debug=configurations.depuration)

    application_fastapi.add_middleware(
        CORSMiddleware,
        allow_origins=configurations.origens_cors,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @application_fastapi.exception_handler(ApplicationError)
    async def handle_application_error(_request: Request, error: ApplicationError) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"detail": error.detail})

    @application_fastapi.get("/health", tags=["system"])
    def verify_password() -> dict[str, str]:
        return {"state": "healthy"}

    application_fastapi.include_router(router_api, prefix=configurations.prefix_api_v1)
    application_fastapi.mount(
        "/archives",
        StaticFiles(directory=configurations.archives_directory),
        name="archives",
    )
    return application_fastapi

app = create_application()
