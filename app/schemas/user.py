from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    cpf: str
    email: str
    birth_date: date
    city: str
    state: str
    is_email_confirmed: bool
    profile_picture_url: str | None


class UserUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=3, max_length=100)
    birth_date: date | None = None
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, pattern=r"^[a-zA-Z]{2}$")

    @field_validator("birth_date")
    @classmethod
    def birth_date_must_be_in_the_past(cls, value: date | None) -> date | None:
        if value is not None and value >= date.today():
            raise ValueError("Birth date must be in the past")
        return value


class PasswordChange(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    current_password: str = Field(min_length=1, max_length=72)
    new_password: str = Field(min_length=6, max_length=72)
    new_password_confirmation: str = Field(min_length=6, max_length=72)
