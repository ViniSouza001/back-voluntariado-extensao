from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserSummary


class VacancyParticipantResponse(BaseModel):
    id: int
    user: UserSummary
    joined_at: datetime
