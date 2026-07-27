from fastapi import APIRouter, status

from app.api.dependencies import CurrentUser, DatabaseSession
from app.schemas.organization import OrganizationCreate, OrganizationResponse
from app.services.organizations import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse, status_code=status.HTTP_201_CREATED)
def create_organization(
    data: OrganizationCreate, current_user: CurrentUser, session: DatabaseSession
) -> OrganizationResponse:
    return OrganizationService(session).create(data, current_user)
