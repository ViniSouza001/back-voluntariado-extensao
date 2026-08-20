from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegistration(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=100)
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    birth_date: date
    city: str = Field(min_length=2, max_length=100)
    uf: str = Field(pattern=r"^[a-zA-Z]{2}$")

    @field_validator("birth_date")
    @classmethod
    def birth_date_must_be_past(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("A data de nascimento deve estar no passado")
        return value


class ResponseToken(BaseModel):
    user: str
    access_token: str
    token_type: str = "bearer"

class ResponseRegister(BaseModel):
    message: str
    confirmation_email_sent: bool

class RequestResendingConfirmation(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
