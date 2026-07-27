from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.email_confirmation import EmailConfirmation


class EmailConfirmationRepository:
    @staticmethod
    def get_by_token_hash(session: Session, token_hash: str) -> EmailConfirmation | None:
        return session.scalar(
            select(EmailConfirmation).where(EmailConfirmation.token_hash == token_hash)
        )

    @staticmethod
    def delete_for_user(session: Session, user_id: int) -> None:
        session.execute(delete(EmailConfirmation).where(EmailConfirmation.user_id == user_id))
