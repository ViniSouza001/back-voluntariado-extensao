from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entity_join_request import EntityJoinRequest, JoinRequestStatus


class RepositoryEntityJoinRequest:
    @staticmethod
    def with_relations():
        return (
            selectinload(EntityJoinRequest.user),
            selectinload(EntityJoinRequest.entity),
            selectinload(EntityJoinRequest.reviewed_by),
        )

    @staticmethod
    def search_for_id(session: Session, id_request: int) -> EntityJoinRequest | None:
        return session.scalar(
            select(EntityJoinRequest)
            .options(*RepositoryEntityJoinRequest.with_relations())
            .where(EntityJoinRequest.id == id_request)
        )

    @staticmethod
    def search_pending(
        session: Session, user_id: int, entity_id: int
    ) -> EntityJoinRequest | None:
        return session.scalar(
            select(EntityJoinRequest).where(
                EntityJoinRequest.user_id == user_id,
                EntityJoinRequest.entity_id == entity_id,
                EntityJoinRequest.status == JoinRequestStatus.PENDING,
            )
        )

    @staticmethod
    def list_for_user(session: Session, user_id: int) -> list[EntityJoinRequest]:
        return list(session.scalars(
            select(EntityJoinRequest)
            .options(*RepositoryEntityJoinRequest.with_relations())
            .where(EntityJoinRequest.user_id == user_id)
            .order_by(EntityJoinRequest.created_at.desc(), EntityJoinRequest.id.desc())
        ).all())

    @staticmethod
    def list_for_entity(
        session: Session, entity_id: int, pending_only: bool
    ) -> list[EntityJoinRequest]:
        query = (
            select(EntityJoinRequest)
            .options(*RepositoryEntityJoinRequest.with_relations())
            .where(EntityJoinRequest.entity_id == entity_id)
            .order_by(EntityJoinRequest.created_at.desc(), EntityJoinRequest.id.desc())
        )
        if pending_only:
            query = query.where(EntityJoinRequest.status == JoinRequestStatus.PENDING)
        return list(session.scalars(query).all())

    @staticmethod
    def other_pending_for_user(
        session: Session, user_id: int, except_id: int
    ) -> list[EntityJoinRequest]:
        return list(session.scalars(
            select(EntityJoinRequest).where(
                EntityJoinRequest.user_id == user_id,
                EntityJoinRequest.id != except_id,
                EntityJoinRequest.status == JoinRequestStatus.PENDING,
            )
        ).all())
