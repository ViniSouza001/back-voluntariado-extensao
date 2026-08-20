from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_configurations
from app.db.session import get_session
from app.models.user import User
from app.repositories.user import RepositoryUser

configurations = get_configurations()
scheme_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{configurations.prefix_api_v1}/auth/login"
)
BaseSession = Annotated[Session, Depends(get_session)]


def get_current_user(
        token: Annotated[str, Depends(scheme_oauth2)], session: BaseSession
) -> User:
    credential_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token de acesso inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_content = jwt.decode(
            token, configurations.secret_key, algorithms=[configurations.algorithm]
        )
        user_identifier = token_content.get("sub")
        if not user_identifier or token_content.get("type") != "user":
            raise credential_error
        id_user = int(user_identifier)
    except (JWTError, TypeError, ValueError) as error:
        raise credential_error from error

    user = RepositoryUser.search_for_id(session, id_user)
    if not user:
        raise credential_error
    return user

ActualUser = Annotated[User, Depends(get_current_user)]