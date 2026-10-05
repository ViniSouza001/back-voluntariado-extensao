from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.entity_join_request import JoinRequestStatus
from app.models.vacancy_join_request import VacancyJoinRequest


class RepositoryVacancyJoinRequest:
    @staticmethod
    def with_relations():
        return (
            selectinload(VacancyJoinRequest.user),
            selectinload(VacancyJoinRequest.vacancy),
            selectinload(VacancyJoinRequest.reviewed_by),
        )

    @staticmethod
    def search_for_id(session: Session, request_id: int) -> VacancyJoinRequest | None:
        return session.scalar(
            select(VacancyJoinRequest)
            .options(*RepositoryVacancyJoinRequest.with_relations())
            .where(VacancyJoinRequest.id == request_id)
        )

    @staticmethod
    def search_pending(
        session: Session, user_id: int, vacancy_id: int
    ) -> VacancyJoinRequest | None:
        return session.scalar(
            select(VacancyJoinRequest).where(
                VacancyJoinRequest.user_id == user_id,
                VacancyJoinRequest.vacancy_id == vacancy_id,
                VacancyJoinRequest.status == JoinRequestStatus.PENDING,
            )
        )

    @staticmethod
    def list_for_user(session: Session, user_id: int) -> list[VacancyJoinRequest]:
        return list(session.scalars(
            select(VacancyJoinRequest)
            .options(*RepositoryVacancyJoinRequest.with_relations())
            .where(VacancyJoinRequest.user_id == user_id)
            .order_by(VacancyJoinRequest.created_at.desc(), VacancyJoinRequest.id.desc())
        ).all())

    @staticmethod
    def list_for_vacancy(
        session: Session, vacancy_id: int, pending_only: bool
    ) -> list[VacancyJoinRequest]:
        query = (
            select(VacancyJoinRequest)
            .options(*RepositoryVacancyJoinRequest.with_relations())
            .where(VacancyJoinRequest.vacancy_id == vacancy_id)
            .order_by(VacancyJoinRequest.created_at.desc(), VacancyJoinRequest.id.desc())
        )
        if pending_only:
            query = query.where(VacancyJoinRequest.status == JoinRequestStatus.PENDING)
        return list(session.scalars(query).all())
