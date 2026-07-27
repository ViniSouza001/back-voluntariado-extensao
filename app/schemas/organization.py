from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class OrganizationCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=100)
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_.-]+$")
    sector: str = Field(min_length=2, max_length=100)
    description: str = Field(min_length=3, max_length=2000)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(pattern=r"^[a-zA-Z]{2}$")


class OrganizationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    username: str
    sector: str
    description: str
    city: str
    state: str
    created_at: date
