from fastapi import APIRouter, status

from app.api.dependencies import DatabaseSession
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    RegistrationResponse,
    ResendConfirmationRequest,
    TokenResponse,
    UserRegistration,
)
from app.schemas.common import MessageResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=RegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegistration, session: DatabaseSession) -> RegistrationResponse:
    _user, email_sent = await AuthService(session).register(data)
    return RegistrationResponse(
        message="Account created. Confirm your email before signing in.",
        confirmation_email_sent=email_sent,
    )


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: DatabaseSession) -> TokenResponse:
    user = AuthService(session).authenticate(str(data.email), data.password)
    return TokenResponse(user=user.name, access_token=create_access_token(user.id))


@router.get("/confirm-email/{token}", response_model=MessageResponse)
def confirm_email(token: str, session: DatabaseSession) -> MessageResponse:
    AuthService(session).confirm_email(token)
    return MessageResponse(message="Email confirmed successfully. You can now sign in.")


@router.post("/resend-confirmation", response_model=MessageResponse)
async def resend_confirmation(
    data: ResendConfirmationRequest, session: DatabaseSession
) -> MessageResponse:
    await AuthService(session).resend_confirmation(str(data.email))
    return MessageResponse(
        message="If an unconfirmed account exists, a new confirmation email will be sent."
    )
