from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    @staticmethod
    def get_by_id(session: Session, user_id: int) -> User | None:
        return session.scalar(select(User).where(User.id == user_id))

    @staticmethod
    def get_by_email(session: Session, email: str) -> User | None:
        return session.scalar(select(User).where(User.email == email.lower()))

    @staticmethod
    def get_by_cpf(session: Session, cpf: str) -> User | None:
        return session.scalar(select(User).where(User.cpf == cpf))

    @staticmethod
    def add(session: Session, user: User) -> User:
        session.add(user)
        return user
