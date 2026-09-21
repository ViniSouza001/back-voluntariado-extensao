from fastapi import APIRouter, Response, status

from app.services.invitations import InvitationService
from app.schemas.invitation import (
    CreateInvitation,
    InvitationListsResponse,
    RespondInvitation,
    ResponseInvitation,
)
from app.api.dependencies import ActualUser, BaseSession


router = APIRouter(prefix="/invitations", tags=["invitations"])


@router.post("", response_model=ResponseInvitation, status_code=status.HTTP_201_CREATED)
def create_invitation(data: CreateInvitation, user: ActualUser, session: BaseSession):
    return InvitationService(session).create_invitation(data, user)


@router.get("", response_model=InvitationListsResponse)
def list_invitations(user: ActualUser, session: BaseSession):
    return InvitationService(session).list_invitations(user)


@router.patch("/{id_invitation}/response", response_model=ResponseInvitation)
def respond_to_invitation(
    id_invitation: int,
    data: RespondInvitation,
    user: ActualUser,
    session: BaseSession,
):
    return InvitationService(session).respond_to_invitation(
        id_invitation, data, user
    )


@router.patch("/{id_invitation}/read", response_model=ResponseInvitation)
def mark_invitation_as_read(
    id_invitation: int,
    user: ActualUser,
    session: BaseSession,
):
    return InvitationService(session).mark_as_read(id_invitation, user)


@router.patch(
    "/{id_invitation}/archive",
    status_code=status.HTTP_204_NO_CONTENT,
)
def archive_invitation(
    id_invitation: int,
    user: ActualUser,
    session: BaseSession,
) -> Response:
    InvitationService(session).archive_invitation(id_invitation, user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
