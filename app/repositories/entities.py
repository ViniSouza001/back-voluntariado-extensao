from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entity import Entity


class RepositoryEntity:
    @staticmethod
    def search_for_username(session: Session, slug: str) -> Entity | None:
        return session.scalar(select(Entity).where(Entity.slug == slug.lower()))

    @staticmethod
    def add(session: Session, entity: Entity) -> Entity:
        session.add(entity)
        return entity