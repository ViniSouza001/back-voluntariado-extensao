from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.dependencies import BaseSession
from app.core.security import create_access_token
from app.schemas.authentication import (
    UserRegistration,
    ResponseRegister,
    ResponseToken,
    RequestResendingConfirmation
)
from app.schemas.commom import ResponseMessage
from app.services.authentication import AuthenticationService

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=ResponseRegister, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegistration, session: BaseSession) -> ResponseRegister:
    _user, confirmation_email_sent = await AuthenticationService(session).register(data)
    return ResponseRegister(
        message="Conta criada. Confirme seu e-mail para fazer login.",
        confirmation_email_sent = confirmation_email_sent
    )


@router.post("/login", response_model=ResponseToken)
def login(
    data: Annotated[OAuth2PasswordRequestForm, Depends()], session: BaseSession
) -> ResponseToken:
    user = AuthenticationService(session).authenticate(data.username, data.password)
    return ResponseToken(user=user.name, access_token=create_access_token(user.id))


@router.get("/confirm-email/{token}", response_model=ResponseMessage)
def confirm_email(token: str, session: BaseSession) -> ResponseMessage:
    AuthenticationService(session).confirm_email(token)
    return ResponseMessage(message="E-mail confirmado, agora você pode fazer login.")


@router.post("/resend-confirmation", response_model=ResponseMessage)
async def resend_confirmation(
    data: RequestResendingConfirmation, session: BaseSession
) -> ResponseMessage:
    await AuthenticationService(session).resend_confirmation(str(data.email))
    return ResponseMessage(
        message="Se existir uma conta não confirmada, um novo e-mail será enviado"
    )
