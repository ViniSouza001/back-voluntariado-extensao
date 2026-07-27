import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AuthenticationError, ConflictError, NotFoundError, ValidationError
from app.core.security import hash_confirmation_token, hash_password, verify_password
from app.models.email_confirmation import EmailConfirmation
from app.models.user import User
from app.repositories.email_confirmations import EmailConfirmationRepository
from app.repositories.users import UserRepository
from app.schemas.auth import UserRegistration
from app.services.email import EmailService
from app.utils.cpf import is_valid_cpf, normalize_cpf


class AuthService:
    def __init__(self, session: Session, email_service: EmailService | None = None):
        self.session = session
        self.email_service = email_service or EmailService()
        self.settings = get_settings()

    async def register(self, data: UserRegistration) -> tuple[User, bool]:
        cpf = normalize_cpf(data.cpf)
        if not is_valid_cpf(cpf):
            raise ValidationError("Invalid CPF")
        if UserRepository.get_by_email(self.session, str(data.email)):
            raise ConflictError("An account with this email already exists")
        if UserRepository.get_by_cpf(self.session, cpf):
            raise ConflictError("An account with this CPF already exists")

        try:
            password_hash = hash_password(data.password)
        except ValueError as error:
            raise ValidationError(str(error)) from error

        user = User(
            name=data.name.strip(),
            cpf=cpf,
            email=str(data.email).lower(),
            password_hash=password_hash,
            birth_date=data.birth_date,
            city=data.city.strip(),
            state=data.state.upper(),
        )
        raw_token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)

        try:
            UserRepository.add(self.session, user)
            self.session.flush()
            self.session.add(
                EmailConfirmation(
                    user_id=user.id,
                    token_hash=hash_confirmation_token(raw_token),
                    created_at=now,
                    expires_at=now
                    + timedelta(minutes=self.settings.email_confirmation_expire_minutes),
                )
            )
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Email or CPF is already registered") from error
        except Exception:
            self.session.rollback()
            raise

        email_sent = await self.email_service.send_confirmation(user.email, raw_token)
        return user, email_sent

    def authenticate(self, email: str, password: str) -> User:
        user = UserRepository.get_by_email(self.session, email)
        if not user or not verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid email or password")
        if not user.is_email_confirmed:
            raise AuthenticationError("Confirm your email before signing in")
        return user

    def confirm_email(self, token: str) -> None:
        confirmation = EmailConfirmationRepository.get_by_token_hash(
            self.session, hash_confirmation_token(token)
        )
        if not confirmation:
            raise NotFoundError("Invalid confirmation token")

        expires_at = confirmation.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=UTC)
        if expires_at < datetime.now(UTC):
            self.session.delete(confirmation)
            self.session.commit()
            raise ValidationError("Confirmation token has expired")

        user = UserRepository.get_by_id(self.session, confirmation.user_id)
        if not user:
            self.session.delete(confirmation)
            self.session.commit()
            raise NotFoundError("User no longer exists")

        user.is_email_confirmed = True
        EmailConfirmationRepository.delete_for_user(self.session, user.id)
        self.session.commit()

    async def resend_confirmation(self, email: str) -> bool:
        user = UserRepository.get_by_email(self.session, email)
        if not user or user.is_email_confirmed:
            return False

        raw_token = secrets.token_urlsafe(32)
        now = datetime.now(UTC)
        EmailConfirmationRepository.delete_for_user(self.session, user.id)
        self.session.add(
            EmailConfirmation(
                user_id=user.id,
                token_hash=hash_confirmation_token(raw_token),
                created_at=now,
                expires_at=now + timedelta(minutes=self.settings.email_confirmation_expire_minutes),
            )
        )
        self.session.commit()
        return await self.email_service.send_confirmation(user.email, raw_token)
