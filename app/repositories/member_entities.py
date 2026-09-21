from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

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

    @staticmethod
    def list_from_entity(
        session: Session,
        id_entity: int,
    ) -> list[MemberEntity]:
        query = (
            select(MemberEntity)
            .options(selectinload(MemberEntity.user))
            .where(MemberEntity.id_entity == id_entity)
            .order_by(MemberEntity.id.asc())
        )
        return list(session.scalars(query).all())

    @staticmethod
    def delete(session: Session, membership: MemberEntity) -> None:
        session.delete(membership)
