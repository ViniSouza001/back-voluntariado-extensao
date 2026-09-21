from fastapi import APIRouter, Response, status

from app.api.dependencies import ActualUser, BaseSession
from app.schemas.entity import EntityCreation, EntityResponse
from app.schemas.entity_membership import EntityMemberResponse, EntityMembershipResponse
from app.schemas.member_position import UpdateMemberPosition, MemberPositionResponse
from app.services.entities import EntityService
from app.services.member_positions import change_member_position as update_position
from app.services.entity_members import EntityMemberService

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


@router.get(
    "/{id_entity}/members",
    response_model=list[EntityMemberResponse],
)
def list_entity_members(
    id_entity: int,
    actual_user: ActualUser,
    session: BaseSession,
):
    return EntityMemberService(session).list_members(id_entity, actual_user)


@router.delete(
    "/{id_entity}/members/{id_user}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_entity_member(
    id_entity: int,
    id_user: int,
    actual_user: ActualUser,
    session: BaseSession,
) -> Response:
    EntityMemberService(session).remove_member(
        id_entity, id_user, actual_user
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete(
    "/{id_entity}/leave",
    status_code=status.HTTP_204_NO_CONTENT,
)
def leave_entity(
    id_entity: int,
    actual_user: ActualUser,
    session: BaseSession,
) -> Response:
    EntityMemberService(session).leave_entity(id_entity, actual_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
def create_entity(
    data: EntityCreation, actual_user: ActualUser, session: BaseSession
) -> EntityResponse:
    return EntityService(session).create(data, actual_user)
