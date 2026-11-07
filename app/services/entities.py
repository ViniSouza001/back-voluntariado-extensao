from datetime import UTC, datetime

from sqlalchemy import distinct, func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.entity import Entity
from app.models.entity_join_request import EntityJoinRequest, JoinRequestStatus
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.user import User
from app.models.vacancy import Vacancies, VacancyModality
from app.models.vacancy_join_request import VacancyJoinRequest
from app.models.vacancy_participant import VacancyParticipant
from app.repositories.entities import RepositoryEntity
from app.repositories.member_entities import RepositoryMemberEntity
from app.schemas.entity import (
    DashboardMembersStats,
    DashboardParticipantsStats,
    DashboardPendingRequestsStats,
    DashboardVacanciesStats,
    EntityCreation,
    EntityDashboardResponse,
)
from app.services.entity_membership import require_entity_position
from app.services.notifications import NotificationService


class EntityService:
    def __init__(self, session: Session):
        self.session = session

    def get_for_user(self, user: User) -> MemberEntity | None:
        return RepositoryMemberEntity.search_by_user(self.session, user.id)

    def get_dashboard(self, id_entity: int, user: User) -> EntityDashboardResponse:
        entity = RepositoryEntity.search_for_id(self.session, id_entity)
        if entity is None:
            raise NotFoundError("Entidade não encontrada")

        require_entity_position(
            self.session,
            user.id,
            id_entity,
            {
                MemberPosition.ADMIN,
                MemberPosition.EDITOR,
                MemberPosition.MEMBER,
            },
        )

        now = datetime.now(UTC).replace(tzinfo=None)
        entity_vacancies = self.session.scalars(
            select(Vacancies).where(Vacancies.id_entity == id_entity)
        ).all()

        total_vacancies = len(entity_vacancies)
        active_vacancies = sum(1 for v in entity_vacancies if v.ends_at >= now)
        ended_vacancies = total_vacancies - active_vacancies
        in_person_vacancies = sum(
            1 for v in entity_vacancies if v.modality == VacancyModality.IN_PERSON
        )
        remote_vacancies = sum(
            1 for v in entity_vacancies if v.modality == VacancyModality.REMOTE
        )

        memberships = RepositoryMemberEntity.list_from_entity(
            self.session, id_entity
        )
        admins_count = sum(
            1 for m in memberships if m.position == MemberPosition.ADMIN
        )
        editors_count = sum(
            1 for m in memberships if m.position == MemberPosition.EDITOR
        )
        members_count = sum(
            1 for m in memberships if m.position == MemberPosition.MEMBER
        )

        total_enrollments = (
            self.session.scalar(
                select(func.count(VacancyParticipant.id))
                .join(Vacancies, VacancyParticipant.id_vacancy == Vacancies.id)
                .where(Vacancies.id_entity == id_entity)
            )
            or 0
        )

        unique_volunteers = (
            self.session.scalar(
                select(func.count(distinct(VacancyParticipant.id_user)))
                .join(Vacancies, VacancyParticipant.id_vacancy == Vacancies.id)
                .where(Vacancies.id_entity == id_entity)
            )
            or 0
        )

        pending_entity_requests = (
            self.session.scalar(
                select(func.count(EntityJoinRequest.id)).where(
                    EntityJoinRequest.entity_id == id_entity,
                    EntityJoinRequest.status == JoinRequestStatus.PENDING,
                )
            )
            or 0
        )

        pending_vacancy_requests = (
            self.session.scalar(
                select(func.count(VacancyJoinRequest.id))
                .join(Vacancies, VacancyJoinRequest.vacancy_id == Vacancies.id)
                .where(
                    Vacancies.id_entity == id_entity,
                    VacancyJoinRequest.status == JoinRequestStatus.PENDING,
                )
            )
            or 0
        )

        return EntityDashboardResponse(
            vacancies=DashboardVacanciesStats(
                total=total_vacancies,
                active=active_vacancies,
                ended=ended_vacancies,
                in_person=in_person_vacancies,
                remote=remote_vacancies,
            ),
            members=DashboardMembersStats(
                total=len(memberships),
                admins=admins_count,
                editors=editors_count,
                members=members_count,
            ),
            participants=DashboardParticipantsStats(
                total_enrollments=total_enrollments,
                unique_volunteers=unique_volunteers,
            ),
            pending_requests=DashboardPendingRequestsStats(
                total=pending_entity_requests + pending_vacancy_requests,
                entity=pending_entity_requests,
                vacancies=pending_vacancy_requests,
            ),
        )

    def create(self, data: EntityCreation, creater: User) -> Entity:
        if RepositoryMemberEntity.search_by_user(self.session, creater.id):
            raise ConflictError("Você já participa de uma entidade")

        slug = data.slug.lower()
        if RepositoryEntity.search_for_slug(self.session, slug):
            raise ConflictError("Já existe uma entidade com este mesmo slug")

        # verificar se a primeira letra da cidade é minúscula
        if data.city[0].islower():
            data.city = data.city.capitalize()

        entity = Entity(
            name = data.name.strip(),
            slug = slug,
            sector = data.sector.strip(),
            description = data.description.strip(),
            city = data.city.strip().title(),
            uf = data.uf.upper()
        )

        try:
            RepositoryEntity.add(self.session, entity)
            self.session.flush()
            self.session.add(
                MemberEntity(
                    id_user=creater.id,
                    id_entity=entity.id,
                    position=MemberPosition.ADMIN,
                )
            )
            NotificationService(self.session).notify_entity_joined(
                creater.id,
                creater.id,
                entity,
            )
            self.session.commit()
            self.session.refresh(entity)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a entidade: usuário ou slug já cadastrado") from error
        except Exception:
            self.session.rollback()
            raise
        return entity
