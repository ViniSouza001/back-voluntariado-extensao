from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class RepositoryUser:
    
    @staticmethod
    def search_for_id(session: Session, id_user: int) -> User | None:
        return session.scalar(select(User).where(User.id == id_user))

    @staticmethod
    def search_for_email(session: Session, email: str) -> User | None:
        return session.scalar(select(User).where(User.email == email.lower()))

    @staticmethod
    def search_for_cpf(session: Session, cpf: str) -> User | None:
        return session.scalar(select(User).where(User.cpf == cpf))

    @staticmethod
    def add(session: Session, user: User) -> User:
        session.add(user)
        return user