from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ResponseUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cpf: str
    email: str
    birth_date: date
    city: str
    uf: str
    confirmed_email: bool


class UpdateUser(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=3, max_length=100)
    birth_date: date | None = None
    city: str | None = Field(default=None, min_length=2, max_length=100)
    uf: str | None = Field(default=None, pattern=r"^[a-zA-Z]{2}$")

    @field_validator("name", "city", "uf")
    @classmethod
    def field_must_not_be_null(cls, value: str | None) -> str:
        if value is None:
            raise ValueError("O campo informado não pode ser nulo")
        return value

    @field_validator("birth_date")
    @classmethod
    def birth_date_must_be_pass(cls, value: date | None) -> date:
        if value is None:
            raise ValueError("A data de nascimento não pode ser nula")
        if value >= date.today():
            raise ValueError("A data de nascimento deve estar no passado")
        return value

class DeleteUser(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    id: int


class UpdatePassword(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=6, max_length=72)
    new_password_confirmation: str = Field(min_length=6, max_length=72)
