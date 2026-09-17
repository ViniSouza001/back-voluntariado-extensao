from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.member_entity import MemberEntity



class RepositoryMemberEntity:
    @staticmethod
    def search_by_user(session: Session, id_user: int) -> MemberEntity | None:
        return session.scalar(
            select(MemberEntity).where(MemberEntity.id_user == id_user)
        )

    @staticmethod
    def search_by_user_and_entity(
        session: Session, id_user: int, id_entity: int
    ) -> MemberEntity | None:
        return session.scalar(
            select(MemberEntity).where(
                MemberEntity.id_user == id_user,
                MemberEntity.id_entity == id_entity,
            )
        )
