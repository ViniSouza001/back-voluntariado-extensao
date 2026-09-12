from app.core.exceptions import ConflictError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ValidationError
from app.models.vacancies import Vacancies, VacancyModality
from app.schemas.vacancies import CreateVacancies, UpdateVacancies
from app.repositories.vacancies import RepositoryVacancy
from app.repositories.entities import RepositoryEntity


class VacancieService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: CreateVacancies) -> Vacancies:
        if not RepositoryEntity.search_for_id(self.session, data.id_entity):
            raise ValidationError("Entidade não encontrada")
            
        vacancy = Vacancies(
            title = data.title.strip(),
            description = data.description.lower(),
            id_entity = int(data.id_entity),
            branch = data.branch.lower().strip(),
            starts_at = data.starts_at,
            ends_at = data.ends_at,

            modality = data.modality
        )

        if data.modality == VacancyModality.IN_PERSON:
            vacancy.city = data.city.lower().strip()
            vacancy.uf = data.uf.upper()
            vacancy.cep = data.cep
            vacancy.thoroughfare = data.thoroughfare.strip()
            vacancy.details = data.details.strip()

        try:
            RepositoryVacancy.create(self.session, vacancy)
            self.session.flush()
            self.session.commit()
            self.session.refresh(vacancy)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível criar a vaga")
        except Exception:
            self.session.rollback()
            raise
        
        return vacancy
        

    def update(self, id_vacancy: int, data: UpdateVacancies) -> Vacancies:
        vacancie = RepositoryVacancy.search(self.session, id = id_vacancy, city = None, uf = None, branch = None, id_entity = None, title = None, modality = None)

        vacancie = vacancie[0] if vacancie else None

        if not vacancie:
            raise ValidationError("Vaga não encontrada")
        
        updates = data.model_dump(exclude_unset=True, exclude_none=True)
        for data_name, value in updates.items():
            # setattr(vacancie, data_name, value)
            setattr(vacancie, data_name, value.strip() if isinstance(value, str) else value)
            
        self.session.commit()
        self.session.refresh(vacancie)
        return vacancie

    def delete(self, id_vacancy: int) -> None:
        vacancie = RepositoryVacancy.search_for_id(self.session, id_vacancy)
        if not vacancie:
            raise ValidationError("Vaga não encontrada")
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