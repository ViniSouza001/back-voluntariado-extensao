from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator

from app.models.entity_join_request import JoinRequestStatus
from app.schemas.user import UserSummary
from app.schemas.vacancy import ResponseVacancies


class DecideVacancyJoinRequest(BaseModel):
    status: JoinRequestStatus

    @field_validator("status")
    @classmethod
    def status_must_be_decision(cls, value: JoinRequestStatus) -> JoinRequestStatus:
        if value not in {JoinRequestStatus.ACCEPTED, JoinRequestStatus.REJECTED}:
            raise ValueError("A decisão deve ser accepted ou rejected")
        return value


class VacancyJoinRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user: UserSummary
    vacancy: ResponseVacancies
    status: JoinRequestStatus
    created_at: datetime
    reviewed_at: datetime | None
    reviewed_by: UserSummary | None
