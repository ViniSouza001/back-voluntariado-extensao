import hashlib
from datetime import UTC, datetime, timedelta

import bcrypt
from jose import jwt

from app.core.config import get_configurations

MAX_BYTES_PASSWORD = 72


def generate_hash_password(password: str) -> str:
    password_in_bytes = password.encode("utf-8")
    if len(password_in_bytes) > MAX_BYTES_PASSWORD:
        raise ValueError("The password cannot exceed 72 bytes")
    return bcrypt.hashpw(password_in_bytes, bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, password_hash: str) -> bool:
    password_in_bytes = password.encode("utf-8")
    if len(password_in_bytes) > MAX_BYTES_PASSWORD:
        return False
    try:
        return bcrypt.checkpw(password_in_bytes, password_hash.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(id_user: int, custom_duration: timedelta | None = None) -> str:
    config = get_configurations()
    expire_at = datetime.now(UTC) + (
        custom_duration or timedelta(minutes = config.minutes_expire_access_token)
    )
    token_content = {"sub": str(id_user), "exp": expire_at, "type": "user"}
    return jwt.encode (
        token_content,
        config.secret_key,
        algorithm=config.algorithm
    )

def generate_hash_confirmation_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
