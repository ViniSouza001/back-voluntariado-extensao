from fastapi import APIRouter, Response, status

from app.api.dependencies import BaseSession, ActualUser
from app.schemas.commom import ResponseMessage
from app.schemas.user import UpdatePassword, UpdateUser, ResponseUser, DeleteUser
from app.services.users import UserService

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=ResponseUser)
def consult_profile(user: ActualUser) -> ResponseUser:
    return user


@router.patch("/me", response_model=ResponseUser)
def update_profile(
    data: UpdateUser, user: ActualUser, session: BaseSession
) -> ResponseUser:
    return UserService(session).update(user, data)


@router.patch("/me/password", response_model=ResponseMessage)
def update_password(
    data: UpdatePassword, user: ActualUser, session: BaseSession
) -> ResponseMessage:
    UserService(session).change_password(user, data)
    return ResponseMessage(message="Sua senha foi alterada com sucesso!")


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(id: DeleteUser, session: BaseSession) -> Response:
    UserService(session).delete(id.id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)