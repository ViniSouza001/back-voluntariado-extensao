from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:
    @staticmethod
    def get_by_username(session: Session, username: str) -> Organization | None:
        return session.scalar(select(Organization).where(Organization.username == username.lower()))

    @staticmethod
    def add(session: Session, organization: Organization) -> Organization:
        session.add(organization)
        return organization
