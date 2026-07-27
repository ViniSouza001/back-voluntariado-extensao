from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserRegistration(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=3, max_length=100)
    cpf: str = Field(min_length=11, max_length=14)
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)
    birth_date: date
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(pattern=r"^[a-zA-Z]{2}$")

    @field_validator("birth_date")
    @classmethod
    def birth_date_must_be_in_the_past(cls, value: date) -> date:
        if value >= date.today():
            raise ValueError("Birth date must be in the past")
        return value


class LoginRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    password: str = Field(min_length=1, max_length=72)


class TokenResponse(BaseModel):
    user: str
    access_token: str
    token_type: str = "bearer"


class RegistrationResponse(BaseModel):
    message: str
    confirmation_email_sent: bool


class ResendConfirmationRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
