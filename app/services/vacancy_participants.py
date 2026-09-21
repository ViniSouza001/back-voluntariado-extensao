from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError
from app.models.member_entity import MemberPosition
from app.models.user import User
from app.models.vacancy import Vacancies
from app.repositories.vacancies import RepositoryVacancy
from app.repositories.vacancy_participants import RepositoryVacancyParticipant
from app.schemas.user import UserSummary
from app.schemas.vacancy_participant import VacancyParticipantResponse
from app.services.entity_membership import require_entity_position
from app.services.notifications import NotificationService


class VacancyParticipantService:
    def __init__(self, session: Session):
        self.session = session

    def _get_vacancy(self, id_vacancy: int) -> Vacancies:
        vacancy = RepositoryVacancy.search_for_id(self.session, id_vacancy)
        if vacancy is None:
            raise NotFoundError("Vaga não encontrada")
        return vacancy

    def list_participants(
        self,
        id_vacancy: int,
        user: User,
    ) -> list[VacancyParticipantResponse]:
        vacancy = self._get_vacancy(id_vacancy)
        require_entity_position(
            self.session,
            user.id,
            vacancy.id_entity,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )

        participants = RepositoryVacancyParticipant.list_from_vacancy(
            self.session, vacancy.id
        )
        return [
            VacancyParticipantResponse(
                id=participant.id,
                user=UserSummary.model_validate(participant.user),
                joined_at=participant.joined_at,
            )
            for participant in participants
        ]

    def leave_vacancy(self, id_vacancy: int, user: User) -> None:
        vacancy = self._get_vacancy(id_vacancy)
        participant = RepositoryVacancyParticipant.search(
            self.session, vacancy.id, user.id
        )
        if participant is None:
            raise NotFoundError("Você não participa desta vaga")

        RepositoryVacancyParticipant.delete(self.session, participant)
        NotificationService(self.session).notify_vacancy_left(
            user.id,
            vacancy,
        )
        self.session.commit()

    def remove_participant(
        self,
        id_vacancy: int,
        id_user: int,
        actor: User,
    ) -> None:
        vacancy = self._get_vacancy(id_vacancy)
        require_entity_position(
            self.session,
            actor.id,
            vacancy.id_entity,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )

        participant = RepositoryVacancyParticipant.search(
            self.session, vacancy.id, id_user
        )
        if participant is None:
            raise NotFoundError("Participante não encontrado nesta vaga")

        RepositoryVacancyParticipant.delete(self.session, participant)
        NotificationService(self.session).notify_vacancy_participant_removed(
            id_user,
            actor.id,
            vacancy,
        )
        self.session.commit()
