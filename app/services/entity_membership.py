from collections.abc import Collection

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenError
from app.models.member_entity import MemberPosition
from app.repositories.member_entities import RepositoryMemberEntity


def get_entity_position(session: Session, id_user: int, id_entity: int) -> MemberPosition:
    """Return the user's role in this entity, or deny access if they do not belong."""
    membership = RepositoryMemberEntity.search_by_user_and_entity(
        session, id_user, id_entity
    )
    if membership is None:
        raise ForbiddenError("Você não pertence a esta entidade")
    return membership.position


def require_entity_position(
    session: Session,
    id_user: int,
    id_entity: int,
    allowed_positions: Collection[MemberPosition],
) -> MemberPosition:
    """Return the role only when it permits the requested operation."""
    position = get_entity_position(session, id_user, id_entity)
    if position not in allowed_positions:
        raise ForbiddenError("Você não tem permissão para executar essa operação")
    return position
