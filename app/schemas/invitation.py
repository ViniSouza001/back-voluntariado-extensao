from datetime import datetime, timezone, timedelta, UTC

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.invitation import Invitation, InvitationStatus, InvitationType
from app.schemas.user import UserSummary

BR_TZ = timezone(timedelta(hours=-3))

class InvitationTarget(BaseModel):
    id: int
    name: str


class ResponseInvitation(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sender: UserSummary
    recipient: UserSummary
    sent_at: datetime
    read_at: datetime | None
    status: InvitationStatus
    invitation_type: InvitationType
    target: InvitationTarget | None = None


class InvitationListsResponse(BaseModel):
    received: list[ResponseInvitation]
    sent: list[ResponseInvitation]


class RespondInvitation(BaseModel):
    status: InvitationStatus

    @field_validator("status")
    @classmethod
    def status_must_be_final(cls, value: InvitationStatus) -> InvitationStatus:
        if value == InvitationStatus.PENDING:
            raise ValueError("A resposta deve ser accepted ou rejected")
        return value


class CreateInvitation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    recipient_id: int
    invitation_type: InvitationType
    target_id: int | None = None
    

    @field_validator("recipient_id", "invitation_type")
    @classmethod
    def field_must_not_be_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("O campo informado não pode ser nulo")
        return value

    @model_validator (mode="after")
    def validate_target(self):
        if self.invitation_type != InvitationType.FRIEND and self.target_id is None:
            raise ValueError("Convites para vagas ou entidades precisam do 'target_id'")
        return self
    
