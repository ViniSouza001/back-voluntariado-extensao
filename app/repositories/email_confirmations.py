from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.email_confirmation import EmailConfirmation


class RepositoryEmailConfirmation:
    @staticmethod
    def search_for_hash_token(session: Session, hash_token: str) -> EmailConfirmation | None:
        return session.scalar(
            select(EmailConfirmation).where(EmailConfirmation.hash_token == hash_token)
        )

    @staticmethod
    def search_for_id_user(session: Session, id_user: int) -> EmailConfirmation | None:
        return session.scalar(
            select(EmailConfirmation).where(EmailConfirmation.id_user == id_user)
        )

    @staticmethod
    def delete_from_user(session: Session, id_user: int) -> None:
        session.execute(delete(EmailConfirmation).where(EmailConfirmation.id_user == id_user))