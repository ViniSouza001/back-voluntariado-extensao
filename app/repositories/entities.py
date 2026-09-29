from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entity import Entity


class RepositoryEntity:
    @staticmethod
    def search(
        session: Session,
        id: int | None,
        name: str | None,
        slug: str | None,
        city: str | None,
        uf: str | None,
        sector: str | None
        ) -> list[Entity]:
        query = select(Entity)

        if id:
            query = query.where(Entity.id == id)
            return session.scalars(query).all()

        if slug:
            query = query.where(Entity.slug == slug)
            return session.scalars(query).all()

        if name:
            query = query.where(Entity.name.ilike(f"%{name.lower().strip()}%"))

        if city:
            query = query.where(Entity.city.ilike(city.strip()))

        if uf:
            query = query.where(Entity.uf == uf.upper().strip())

        if sector:
            query = query.where(Entity.sector == sector.strip())

        return session.scalars(query).all()

    @staticmethod
    def search_for_slug(session: Session, slug: str) -> Entity | None:
        return session.scalar(select(Entity).where(Entity.slug == slug.lower()))

    @staticmethod
    def add(session: Session, entity: Entity) -> Entity:
        session.add(entity)
        return entity

    @staticmethod
    def search_for_id(session: Session, id_entity: int) -> Entity | None:
        return session.scalar(select(Entity).where(Entity.id == id_entity))
