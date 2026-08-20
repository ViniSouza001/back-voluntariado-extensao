from fastapi import APIRouter, status

from app.api.dependencies import ActualUser, BaseSession
from app.schemas.entity import EntityCreation, EntityResponse
from app.services.entities import EntityService

router = APIRouter(prefix="/entities", tags=["entities"])


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    data: EntityCreation, actual_user: ActualUser, session: BaseSession
) -> EntityResponse:
    return EntityService(session).create(data, actual_user)