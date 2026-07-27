from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationError, ValidationError
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import PasswordChange, UserUpdate


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def update(self, user: User, data: UserUpdate) -> User:
        changes = data.model_dump(exclude_unset=True)
        if "state" in changes and changes["state"] is not None:
            changes["state"] = changes["state"].upper()
        for field_name, value in changes.items():
            setattr(user, field_name, value.strip() if isinstance(value, str) else value)
        self.session.commit()
        self.session.refresh(user)
        return user

    def change_password(self, user: User, data: PasswordChange) -> None:
        if not verify_password(data.current_password, user.password_hash):
            raise AuthenticationError("Current password is incorrect")
        if data.new_password != data.new_password_confirmation:
            raise ValidationError("New passwords do not match")
        if verify_password(data.new_password, user.password_hash):
            raise ValidationError("New password must be different from the current password")
        try:
            user.password_hash = hash_password(data.new_password)
        except ValueError as error:
            raise ValidationError(str(error)) from error
        self.session.commit()

    def delete(self, user: User) -> None:
        self.session.delete(user)
        self.session.commit()
