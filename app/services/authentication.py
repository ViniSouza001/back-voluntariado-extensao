import secrets
from datetime import UTC, datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import get_configurations
from app.core.exceptions import (
    ApplicationError,
    ConflictError,
    NotFoundError,
    ValidationError,
    AuthenticationError,
)
from app.core.security import (
    generate_hash_password,
    generate_hash_confirmation_token,
    verify_password
)
from app.models.email_confirmation import EmailConfirmation
from app.models.user import User
from app.repositories.email_confirmations import RepositoryEmailConfirmation
from app.repositories.user import RepositoryUser
from app.schemas.authentication import UserRegistration
from app.services.email import EmailService
from app.utils.cpf import valid_cpf, normalize_cpf


class AuthenticationService:
    def __init__(self, session: Session, email_service: EmailService | None = None) -> None:
        self.session = session

        if email_service is None:
            self.email_service = EmailService()
        else:
            self.email_service = email_service

        self.configurations = get_configurations()

    async def register(self, data: UserRegistration) -> tuple[User, bool]:
        cpf = normalize_cpf(data.cpf)
        if not valid_cpf(cpf):
            raise ValidationError("CPF inválido")
        if RepositoryUser.search_for_cpf(self.session, cpf):
            raise ConflictError("Já existe um cadastro com este CPF")
        if RepositoryUser.search_for_email(self.session, str(data.email)):
            raise ConflictError("Já existe um cadastro com este e-mail")

        try:
            password_hash = generate_hash_password(data.password)
        except ValueError as error:
            raise ValidationError(str(error)) from error

        now = datetime.now(UTC)

        user = User (
            name=data.name.strip(),
            cpf=cpf,
            email=str(data.email).lower(),
            password=password_hash,
            birth_date=data.birth_date,
            city=data.city.strip(),
            uf=data.uf.upper(),
        )
        original_token = secrets.token_urlsafe(32)

        try:
            RepositoryUser.add(self.session, user)
            self.session.flush()
            self.session.add(
                EmailConfirmation(
                    id_user=user.id,
                    hash_token=generate_hash_confirmation_token(original_token),
                    created_at=now,
                    expire_at=now + timedelta(minutes=self.configurations.minutes_expire_confirmation_email),
                    resend_at=now + timedelta(minutes=self.configurations.minutes_resend_confirmation_email),
                )
            )
            self.session.commit()
            self.session.refresh(user)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("O e-mail ou CPF já está cadastrado") from error
        except Exception:
            self.session.rollback()
            raise

        sent_email = await self.email_service.send_confirmation(user.email, original_token)
        return user, sent_email

    def authenticate(self, email: str, password: str) -> User:
        user = RepositoryUser.search_for_email(self.session, email)
        if not user or not verify_password(password, user.password):
            raise AuthenticationError("E-mail ou senha inválidos")
        if not user.confirmed_email:
            raise AuthenticationError("Confirme seu e-mail para fazer login")
        return user

    def confirm_email(self, token: str):
        confirmation = RepositoryEmailConfirmation.search_for_hash_token(self.session, generate_hash_confirmation_token(token))
        if not confirmation:
            raise NotFoundError("Token de confirmação inválido")

        expire_at = confirmation.expire_at
        if expire_at.tzinfo is None:
            expire_at = expire_at.replace(tzinfo=UTC)
        if expire_at < datetime.now(UTC):
            raise ValidationError("O token de confirmação está expirado")

        user = RepositoryUser.search_for_id(self.session, confirmation.id_user)
        if not user:
            self.session.delete(confirmation)
            self.session.commit()
            raise NotFoundError("O usuário não existe mais")

        user.confirmed_email = True
        RepositoryEmailConfirmation.delete_from_user(self.session, user.id)
        self.session.commit()

    async def resend_confirmation(self, email: str) -> bool:
        user = RepositoryUser.search_for_email(self.session, email)
        if not user or user.confirmed_email:
            return False
        print(user.id)
        confirmation = RepositoryEmailConfirmation.search_for_id_user(self.session, user.id)

        if not confirmation:
            return False

        now = datetime.now(UTC)
        resend_at = confirmation.resend_at

        if resend_at is not None:
            if resend_at.tzinfo is None:
                resend_at = resend_at.replace(tzinfo=UTC)

        if now < resend_at:
            raise ValidationError("Aguarde antes de solicitar outra confirmação")

        original_token = secrets.token_urlsafe(32)

        confirmation.hash_token = generate_hash_confirmation_token(original_token)
        confirmation.created_at = now
        confirmation.expire_at = now + timedelta(minutes=self.configurations.minutes_expire_confirmation_email)
        confirmation.resend_at = now + timedelta(minutes=self.configurations.minutes_resend_confirmation_email)

        self.session.commit()

        return await self.email_service.send_confirmation(user.email, original_token)
