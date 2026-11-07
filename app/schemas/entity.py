from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class EntityCreation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=100)
    slug: str = Field(min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_.-]+$")
    sector: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=3, max_length=2000)
    city: str = Field(min_length=2, max_length=100)
    uf: str = Field(pattern=r"^[a-zA-Z]{2}$")


class EntityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sector: str
    description: str
    city: str
    uf: str
    created_at: date

class EntityList(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    sector: str
    description: str
    city: str
    uf: str
    created_at: date

class EntitySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str


class DashboardVacanciesStats(BaseModel):
    total: int
    active: int
    ended: int
    in_person: int
    remote: int


class DashboardMembersStats(BaseModel):
    total: int
    admins: int
    editors: int
    members: int


class DashboardParticipantsStats(BaseModel):
    total_enrollments: int
    unique_volunteers: int


class DashboardPendingRequestsStats(BaseModel):
    total: int
    entity: int
    vacancies: int


class EntityDashboardResponse(BaseModel):
    vacancies: DashboardVacanciesStats
    members: DashboardMembersStats
    participants: DashboardParticipantsStats
    pending_requests: DashboardPendingRequestsStats
