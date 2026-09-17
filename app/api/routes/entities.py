from fastapi import APIRouter, status

from app.api.dependencies import ActualUser, BaseSession
from app.schemas.entity import EntityCreation, EntityResponse
from app.schemas.entity_membership import EntityMembershipResponse
from app.schemas.member_positions import UpdateMemberPosition, MemberPositionResponse
from app.services.entities import EntityService
from app.services.member_positions import change_member_position as update_position

router = APIRouter(prefix="/entities", tags=["entities"])


@router.get("/me", response_model=EntityMembershipResponse | None)
def get_my_entity(actual_user: ActualUser, session: BaseSession):
    return EntityService(session).get_for_user(actual_user)



@router.patch("/{id_entity}/members/{id_user}/position", response_model=MemberPositionResponse)
def change_member_position(
    id_entity: int,
    id_user: int,
    data: UpdateMemberPosition,
    actual_user: ActualUser,
    session: BaseSession,
):
    return update_position(session, id_entity, id_user, data.position, actual_user)


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    data: EntityCreation, actual_user: ActualUser, session: BaseSession
) -> EntityResponse:
    return EntityService(session).create(data, actual_user)