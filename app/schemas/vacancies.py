from datetime import datetime, timezone, timedelta, UTC

from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer, model_validator

from app.models.vacancies import VacancyModality

BR_TZ = timezone(timedelta(hours=-3))
UTC_TZ = timezone(timedelta(hours=+3))

class ResponseVacancies(BaseModel):
    id: int
    title: str
    description: str
    posted_at: datetime
    starts_at: datetime
    ends_at: datetime
    branch: str

    modality: VacancyModality

    cep: str | None
    number: str | None
    thoroughfare: str | None
    details: str | None

    city: str | None
    uf: str | None
    model_config = ConfigDict(from_attributes=True)

    @field_serializer("posted_at", "starts_at", "ends_at", when_used="json")
    def serialize_to_brasilia_tz(self, dt: datetime) -> str:
        # Se o banco retornar naive datetime, consideramos que está em UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(BR_TZ).isoformat()

class CreateVacancies(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    title: str = Field(min_length=3, max_length=100)
    description: str = Field(min_length=1, max_length=255)
    id_entity: int
    starts_at: datetime
    ends_at: datetime
    branch: str = Field(min_length=1, max_length=50)

    modality: VacancyModality

    cep: str | None= Field(default=None, min_length=8, max_length=8)
    number: str | None = Field(default=None, min_length=1, max_length=50)
    thoroughfare: str | None = Field(default=None, min_length=1, max_length=100)
    details: str | None = Field(default=None, min_length=1, max_length=100)

    city: str | None = Field(default=None, min_length=1, max_length=100)
    uf: str | None = Field(default=None, min_length=2, max_length=2)

    @field_validator("title", "description", "branch")
    @classmethod
    def field_must_not_be_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("O campo informado não pode ser nulo")
        return value

    @field_validator("starts_at", "ends_at")
    @classmethod
    def date_must_be_future(cls, value: datetime | None) -> datetime:
        if value is None:
            raise ValueError("A data não pode ser nula")
            
        # Se o usuário enviar sem timezone explícito, assume horário de Brasília (UTC-3)
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        
        if value <= now:
            raise ValueError("A data deve estar no futuro")
           
        return value.astimezone(UTC_TZ)

    @model_validator(mode="after")
    def validate_location(self):
        if self.modality == VacancyModality.IN_PERSON:
            if not self.thoroughfare or not self.city or not self.uf:
                raise ValueError("Vagas presenciais precisam de logradouro, cidade e UF")
        return self


class UpdateVacancies(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "title": "Novo título",
            }
        },
    )
    
    title: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=255)
    branch: str | None = Field(default=None, min_length=1, max_length=50)

    modality: VacancyModality | None = None

    cep: str | None= Field(default=None, min_length=8, max_length=8)
    number: str | None = Field(default=None, min_length=1, max_length=50)
    thoroughfare: str | None = Field(default=None, min_length=1, max_length=100)
    details: str | None = Field(default=None, min_length=1, max_length=100)

    city: str | None = Field(default=None, min_length=1, max_length=100)
    uf: str | None = Field(default=None, min_length=2, max_length=2)

    @model_validator(mode="after")
    def validate_location(self):
        if self.modality == VacancyModality.IN_PERSON:
            if not self.thoroughfare or not self.city or not self.uf:
                raise ValueError("Vagas presenciais precisam de logradouro, cidade e UF")
        return self

class DeleteVacancies(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int

class ListVacancies(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    posted_at: datetime
    starts_at: datetime
    ends_at: datetime
    branch: str

    modality: VacancyModality

    cep: str | None
    number: str | None
    thoroughfare: str | None
    details: str | None

    city: str | None
    uf: str | None

    @field_serializer("posted_at", "starts_at", "ends_at", when_used="json")
    def serialize_to_brasilia_tz(self, dt: datetime) -> str:
        # Se o banco retornar naive datetime, consideramos que está em UTC
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(BR_TZ).isoformat()