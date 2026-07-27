from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.models.organization import Organization
from app.models.organization_member import MemberRole, OrganizationMember
from app.models.user import User
from app.repositories.organizations import OrganizationRepository
from app.schemas.organization import OrganizationCreate


class OrganizationService:
    def __init__(self, session: Session):
        self.session = session

    def create(self, data: OrganizationCreate, creator: User) -> Organization:
        username = data.username.lower()
        if OrganizationRepository.get_by_username(self.session, username):
            raise ConflictError("An organization with this username already exists")

        organization = Organization(
            name=data.name.strip(),
            username=username,
            sector=data.sector.strip(),
            description=data.description.strip(),
            city=data.city.strip(),
            state=data.state.upper(),
        )
        try:
            OrganizationRepository.add(self.session, organization)
            self.session.flush()
            self.session.add(
                OrganizationMember(
                    user_id=creator.id,
                    organization_id=organization.id,
                    role=MemberRole.ADMIN,
                )
            )
            self.session.commit()
            self.session.refresh(organization)
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Organization username is already in use") from error
        except Exception:
            self.session.rollback()
            raise
        return organization
