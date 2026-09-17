from sqlalchemy.ext.asyncio import session
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vacancies import Vacancies, VacancyModality


class RepositoryVacancy:
    
    @staticmethod
    def search_for_id(session: Session, id_vacancy: int) -> Vacancies | None:
        return session.get(Vacancies, id_vacancy)

    @staticmethod
    def create(session: Session, vacancie: Vacancies) -> Vacancies:
        session.add(vacancie)
        return vacancie
    
    @staticmethod
    def delete(session: Session, vacancie: Vacancies) -> Vacancies:
        session.delete(vacancie)
        return vacancie
    
    @staticmethod
    def update(session: Session, vacancie: Vacancies) -> Vacancies:
        session.add(vacancie)
        return vacancie

    @staticmethod
    def search(
        session: Session,
        id: int | None,
        city: str | None,
        uf: str | None,
        branch: str | None,
        id_entity: int | None,
        title: str | None,
        modality: VacancyModality | None
    ) -> list[Vacancies]:

        query = select(Vacancies)

        if id:
            query = query.where(Vacancies.id == id)
            return session.scalars(query).all()

        if city:
            query = query.where(Vacancies.city == city.lower().strip())
        if uf:
            query = query.where(Vacancies.uf == uf.upper())
        if branch:
            query = query.where(Vacancies.branch == branch.lower().strip())
        if id_entity:
            query = query.where(Vacancies.id_entity == id_entity)
        if title:
            query = query.where(Vacancies.title.ilike(f"%{title.lower().strip()}%"))
        if modality:
            query = query.where(Vacancies.modality == modality)

        return session.scalars(query).all()