from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.vacancy_participant import VacancyParticipant


class RepositoryVacancyParticipant:
    @staticmethod
    def search(
        session: Session,
        id_vacancy: int,
        id_user: int,
    ) -> VacancyParticipant | None:
        return session.scalar(
            select(VacancyParticipant).where(
                VacancyParticipant.id_vacancy == id_vacancy,
                VacancyParticipant.id_user == id_user,
            )
        )

    @staticmethod
    def create(
        session: Session,
        participant: VacancyParticipant,
    ) -> VacancyParticipant:
        session.add(participant)
        return participant

    @staticmethod
    def list_from_vacancy(
        session: Session,
        id_vacancy: int,
    ) -> list[VacancyParticipant]:
        query = (
            select(VacancyParticipant)
            .options(selectinload(VacancyParticipant.user))
            .where(VacancyParticipant.id_vacancy == id_vacancy)
            .order_by(VacancyParticipant.joined_at.asc())
        )
        return list(session.scalars(query).all())

    @staticmethod
    def delete(
        session: Session,
        participant: VacancyParticipant,
    ) -> None:
        session.delete(participant)
