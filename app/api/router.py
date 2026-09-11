from fastapi import APIRouter

from app.api.routes import authentication, entities, users, vacancies

router_api = APIRouter()

router_api.include_router(authentication.router)
router_api.include_router(entities.router)
router_api.include_router(users.router)
router_api.include_router(vacancies.router)