from sqlalchemy.ext.asyncio import session
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.vacancies import Vacancies


class RepositoryVacancy:
    
    @staticmethod
    def list(session: Session) -> list[Vacancies]:
        return session.scalars(select(Vacancies).order_by(Vacancies.id.desc())).all()
    
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
    def search_for_id(session: Session, id_vacancy: int) -> Vacancies | None:
        return session.scalar(select(Vacancies).where(Vacancies.id == id_vacancy))
    

    @staticmethod
    def search_for_title(session: Session, title: str) -> list[Vacancies]:
        return session.scalars(select(Vacancies).where(Vacancies.title.like(f"%{title}%"))).all()

    @staticmethod
    def search_for_entity(session: Session, id_entity: int) -> list[Vacancies]:
        return session.scalars(select(Vacancies).where(Vacancies.id_entity == id_entity)).all()

    @staticmethod
    def search_for_location(session: Session, city: str | None, uf: str | None) -> list[Vacancies]:
        query = select(Vacancies)

        if uf:
            query = query.where(Vacancies.uf == uf.upper().strip())
        if city:
            query = query.where(Vacancies.city.ilike(f"%{city.strip()}%"))

        return session.scalars(query.order_by(Vacancies.id.desc())).all()

    @staticmethod
    def search_for_branch(session: Session, branch: str) -> list[Vacancies]:
        return session.scalars(select(Vacancies).where(Vacancies.branch == branch.strip())).all()
    