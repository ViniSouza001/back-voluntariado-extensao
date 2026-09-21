from app.core.exceptions import ConflictError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ValidationError
from app.models.member_entity import MemberPosition
from app.models.vacancy import Vacancies, VacancyModality, VacancyBranch
from app.models.user import User
from app.schemas.vacancy import CreateVacancies, UpdateVacancies
from app.repositories.vacancies import RepositoryVacancy
from app.repositories.entities import RepositoryEntity
from app.services.entity_membership import require_entity_position
from app.repositories.vacancy_participants import RepositoryVacancyParticipant
from app.services.notifications import NotificationService


class VacancieService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: CreateVacancies, user: User) -> Vacancies:
        # identificar entidade
        entity = RepositoryEntity.search_for_id(self.session, data.id_entity)
        if not entity:
            raise ValidationError("Entidade não encontrada")

        require_entity_position(
            self.session, user.id, entity.id,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )

        vacancy = Vacancies(
            title = data.title.strip(),
            description = data.description.lower(),
            id_entity = int(data.id_entity),
            branch = data.branch,
            starts_at = data.starts_at,
            ends_at = data.ends_at,

            modality = data.modality
        )

        if data.modality == VacancyModality.IN_PERSON:
            vacancy.city = data.city.lower().strip()
            vacancy.uf = data.uf.upper()
            vacancy.cep = data.cep
            vacancy.number = data.number
            vacancy.thoroughfare = data.thoroughfare.strip()
            vacancy.details = data.details.strip() if data.details else None

        try:
            RepositoryVacancy.create(self.session, vacancy)
            self.session.flush()
            NotificationService(self.session).notify_vacancy_created(
                user.id,
                vacancy,
            )
            self.session.commit()
            self.session.refresh(vacancy)
        except IntegrityError:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a vaga")
        except Exception:
            self.session.rollback()
            raise
        
        return vacancy
        

    def update(self, id_vacancy: int, data: UpdateVacancies, user: User) -> Vacancies:
        vacancie = RepositoryVacancy.search_for_id(self.session, id_vacancy)
        if not vacancie:
            raise ValidationError("Vaga não encontrada")

        require_entity_position(
            self.session, user.id, vacancie.id_entity,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )
        
        updates = data.model_dump(exclude_unset=True, exclude_none=True)
        vacancy_changed = any(
            getattr(vacancie, data_name) != value
            for data_name, value in updates.items()
        )
        for data_name, value in updates.items():
            setattr(vacancie, data_name, value.strip() if isinstance(value, str) else value)

        if vacancy_changed:
            participants = RepositoryVacancyParticipant.list_from_vacancy(
                self.session, vacancie.id
            )
            notification_service = NotificationService(self.session)
            for participant in participants:
                notification_service.notify_vacancy_updated(
                    participant.id_user,
                    user.id,
                    vacancie,
                )

        self.session.commit()
        self.session.refresh(vacancie)
        return vacancie

    def delete(self, id_vacancy: int, user: User) -> None:
        vacancie = RepositoryVacancy.search_for_id(self.session, id_vacancy)
        if not vacancie:
            raise ValidationError("Vaga não encontrada")

        require_entity_position(
            self.session, user.id, vacancie.id_entity,
            {MemberPosition.ADMIN, MemberPosition.EDITOR},
        )

        participants = RepositoryVacancyParticipant.list_from_vacancy(
            self.session, vacancie.id
        )
        notification_service = NotificationService(self.session)
        for participant in participants:
            notification_service.notify_vacancy_deleted(
                participant.id_user,
                user.id,
                vacancie.title,
            )

        self.session.delete(vacancie)
        self.session.commit()

    def list(
            self,
            id: int | None,
            city: str | None,
            uf: str | None,
            branch: str | None,
            id_entity: int | None,
            title: str | None,
            modality: VacancyModality | None

            ) -> list[Vacancies]:

        return RepositoryVacancy.search(
            self.session,
            id = id,
            city = city,
            uf = uf,
            branch = branch,
            id_entity = id_entity,
            title = title,
            modality = modality
        )
