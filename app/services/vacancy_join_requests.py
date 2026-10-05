from datetime import UTC, datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.entity_join_request import JoinRequestStatus
from app.models.member_entity import MemberPosition
from app.models.user import User
from app.models.vacancy import Vacancies
from app.models.vacancy_join_request import VacancyJoinRequest
from app.models.vacancy_participant import VacancyParticipant
from app.repositories.member_entities import RepositoryMemberEntity
from app.repositories.vacancies import RepositoryVacancy
from app.repositories.vacancy_join_requests import RepositoryVacancyJoinRequest
from app.repositories.vacancy_participants import RepositoryVacancyParticipant
from app.services.entity_membership import require_entity_position
from app.services.notifications import NotificationService


class VacancyJoinRequestService:
    def __init__(self, session: Session):
        self.session = session

    def _get_vacancy(self, vacancy_id: int) -> Vacancies:
        vacancy = RepositoryVacancy.search_for_id(self.session, vacancy_id)
        if vacancy is None:
            raise NotFoundError("Vaga não encontrada")
        return vacancy

    def create(self, vacancy_id: int, user: User) -> VacancyJoinRequest:
        vacancy = self._get_vacancy(vacancy_id)
        if vacancy.ends_at <= datetime.now(UTC).replace(tzinfo=None):
            raise ConflictError("Esta vaga já foi encerrada")
        if RepositoryVacancyParticipant.search(self.session, vacancy_id, user.id):
            raise ConflictError("Você já participa desta vaga")
        if RepositoryVacancyJoinRequest.search_pending(self.session, user.id, vacancy_id):
            raise ConflictError("Você já possui uma solicitação pendente para esta vaga")
        if not vacancy.requires_approval:
            request = VacancyJoinRequest(
                user_id=user.id, 
                vacancy_id=vacancy_id,
                status=JoinRequestStatus.ACCEPTED,
                reviewed_at=datetime.now(UTC).replace(tzinfo=None)
            )
            participant = VacancyParticipant(id_vacancy=vacancy_id, id_user=user.id)
            try:
                self.session.add(request)
                RepositoryVacancyParticipant.create(self.session, participant)
                self.session.commit()
                self.session.refresh(request)
                return RepositoryVacancyJoinRequest.search_for_id(self.session, request.id)
            except IntegrityError as error:
                self.session.rollback()
                raise ConflictError("Não foi possível processar a entrada na vaga") from error
            except Exception:
                self.session.rollback()
                raise

        request = VacancyJoinRequest(user_id=user.id, vacancy_id=vacancy_id)
        try:
            self.session.add(request)
            self.session.flush()
            notifications = NotificationService(self.session)
            for membership in RepositoryMemberEntity.list_from_entity(
                self.session, vacancy.id_entity
            ):
                if (
                    membership.position in {MemberPosition.ADMIN, MemberPosition.EDITOR}
                    and membership.id_user != user.id
                ):
                    notifications.notify_vacancy_join_requested(membership.id_user, request)
            self.session.commit()
            self.session.refresh(request)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a solicitação") from error
        except Exception:
            self.session.rollback()
            raise
        return RepositoryVacancyJoinRequest.search_for_id(self.session, request.id)

    def list_for_user(self, user: User) -> list[VacancyJoinRequest]:
        return RepositoryVacancyJoinRequest.list_for_user(self.session, user.id)

    def list_for_vacancy(
        self, vacancy_id: int, actor: User, pending_only: bool = True
    ) -> list[VacancyJoinRequest]:
        vacancy = self._get_vacancy(vacancy_id)
        require_entity_position(
            self.session, actor.id, vacancy.id_entity,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )
        return RepositoryVacancyJoinRequest.list_for_vacancy(
            self.session, vacancy_id, pending_only
        )

    def decide(
        self, vacancy_id: int, request_id: int, decision: JoinRequestStatus,
        actor: User,
    ) -> VacancyJoinRequest:
        vacancy = self._get_vacancy(vacancy_id)
        require_entity_position(
            self.session, actor.id, vacancy.id_entity,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )
        request = RepositoryVacancyJoinRequest.search_for_id(self.session, request_id)
        if request is None or request.vacancy_id != vacancy_id:
            raise NotFoundError("Solicitação não encontrada")
        if request.status != JoinRequestStatus.PENDING:
            raise ConflictError("Esta solicitação já foi encerrada")

        if decision == JoinRequestStatus.ACCEPTED:
            if vacancy.ends_at <= datetime.now(UTC).replace(tzinfo=None):
                raise ConflictError("Esta vaga já foi encerrada")
            if RepositoryVacancyParticipant.search(
                self.session, vacancy_id, request.user_id
            ):
                raise ConflictError("O usuário já participa desta vaga")
            RepositoryVacancyParticipant.create(
                self.session,
                VacancyParticipant(id_vacancy=vacancy_id, id_user=request.user_id),
            )

        request.status = decision
        request.reviewed_at = datetime.now(UTC).replace(tzinfo=None)
        request.reviewed_by_id = actor.id

        try:
            if decision == JoinRequestStatus.ACCEPTED:
                NotificationService(self.session).notify_vacancy_joined(
                    request.user_id, actor.id, vacancy
                )
            self.session.commit()
            self.session.refresh(request)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível decidir a solicitação") from error
        except Exception:
            self.session.rollback()
            raise
        return request
