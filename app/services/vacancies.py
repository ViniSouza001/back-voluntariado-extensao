from app.core.exceptions import ConflictError
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import ValidationError
from app.models.vacancies import Vacancies
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
            address = data.address.lower(),
            branch = data.branch.lower().strip(),
            city = data.city.lower().strip(),
            uf = data.uf.upper(),
            starts_at = data.starts_at,
            ends_at = data.ends_at
        )

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
        

    def update(self, vacancie: Vacancies, data: UpdateVacancies) -> Vacancies:
        updates = data.model_dump(exclude_unset=True)
        for data_name, value in updates.items():
            setattr(vacancie, data_name, value)
        self.session.commit()
        self.session.refresh(vacancie)
        return vacancie
    

    def delete(self, id_vacancy: int) -> None:
        vacancie = RepositoryVacancy.search_for_id(self.session, id_vacancy)
        if not vacancie:
            raise ValidationError("Vaga não encontrada")
        self.session.delete(vacancie)
        self.session.commit()

    def list(self, city: str | None, uf: str | None, branch: str | None, id_entity: int | None, title: str | None) -> list[Vacancies]:
        if city or uf:
            available_vacancies = RepositoryVacancy.search_for_location(self.session, city, uf)
        elif branch:
            available_vacancies = RepositoryVacancy.search_for_branch(self.session, branch)
        elif id_entity:
            available_vacancies = RepositoryVacancy.search_for_entity(self.session, id_entity)
        elif title:
            available_vacancies = RepositoryVacancy.search_for_title(self.session, title)
        else:
            available_vacancies = RepositoryVacancy.list(self.session)
            
        return available_vacancies


        ## combinações de pesquisa
        # segundo Gemini, posso fazer uma combinação de listagem (por exemplo pesquisar por local e área de atuação)
        # e fazer um método no repositório que vá concatenando os filtros na mesma query

    
    