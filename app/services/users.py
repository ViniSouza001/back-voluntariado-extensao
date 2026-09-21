from sqlalchemy.orm import Session

from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AuthenticationError, ConflictError, ValidationError
from app.core.security import generate_hash_password, verify_password
from app.models.user import User
from app.repositories.users import RepositoryUser
from app.repositories.invitations import RepositoryInvitation
from app.schemas.user import UpdatePassword, UpdateUser


class UserService:
    def __init__(self, session: Session):
        self.session = session

    def update(self, user: User, data: UpdateUser) -> User:
        # PATCH deve alterar somente os campos enviados pelo cliente. Como os
        # campos da tabela users são obrigatórios, null também não deve apagar
        # o valor já persistido.
        updates = data.model_dump(exclude_unset=True, exclude_none=True)

        if "uf" in updates and updates["uf"] is not None:
            updates["uf"] = updates["uf"].upper()

        for data_name, value in updates.items():
            setattr(user, data_name, value.strip() if isinstance(value, str) else value)
        self.session.commit()
        self.session.refresh(user)
        return user


    def change_password(self, user: User, data: UpdatePassword) -> None:
        if not verify_password(data.current_password, user.password):
            raise AuthenticationError("A senha atual está incorreta")
        if data.new_password != data.new_password_confirmation:
            raise ValidationError("As senhas não coincidem")
        if verify_password(data.new_password, user.password):
            raise ValidationError("A nova senha deve ser diferente da senha atual")

        try:
            user.password = generate_hash_password(data.new_password)
        except ValueError as error:
            raise ValidationError(str(error)) from error
        self.session.commit()

    def delete(self, id_user: int) -> None:
        user = RepositoryUser.search_for_id(self.session, id_user)
        if user is None:
            raise ValidationError("Usuário não encontrado")

        try:
            # Convites possuem duas chaves estrangeiras para users. Eles precisam
            # ser removidos antes da conta para não violar a integridade do banco.
            RepositoryInvitation.delete_from_user(self.session, user.id)
            self.session.delete(user)
            self.session.commit()
        except IntegrityError as error:
            self.session.rollback()
            raise ConflictError("Não foi possível excluir o usuário") from error
        except Exception:
            self.session.rollback()
            raise
