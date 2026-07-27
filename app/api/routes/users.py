from fastapi import APIRouter, Response, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.common import MessageResponse
from app.schemas.user import PasswordChange, UserResponse, UserUpdate
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def get_profile(current_user: CurrentUser) -> UserResponse:
    return current_user


@router.patch("/me", response_model=UserResponse)
def update_profile(
    data: UserUpdate, current_user: CurrentUser, session: DatabaseSession
) -> UserResponse:
    return UserService(session).update(current_user, data)


@router.patch("/me/password", response_model=MessageResponse)
def change_password(
    data: PasswordChange, current_user: CurrentUser, session: DatabaseSession
) -> MessageResponse:
    UserService(session).change_password(current_user, data)
    return MessageResponse(message="Password changed successfully")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(current_user: CurrentUser, session: DatabaseSession) -> Response:
    UserService(session).delete(current_user)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
