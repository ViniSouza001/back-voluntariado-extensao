from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.models.member_entity import MemberEntity, MemberPosition
from app.models.user import User
from app.repositories.member_entity import RepositoryMemberEntity
from app.repositories.member_positions import count_entity_admins
from app.services.entity_membership import require_entity_position


def change_member_position(
    session: Session,
    id_entity: int,
    id_user: int,
    new_position: MemberPosition,
    actor: User,
) -> MemberEntity:
    require_entity_position(session, actor.id, id_entity, {MemberPosition.ADMIN})

    membership = RepositoryMemberEntity.search_by_user_and_entity(
        session, id_user, id_entity
    )
    if membership is None:
        raise NotFoundError("Membro não encontrado nesta entidade")

    if (
        membership.position == MemberPosition.ADMIN
        and new_position != MemberPosition.ADMIN
        and count_entity_admins(session, id_entity) == 1
    ):
        raise ConflictError("A entidade precisa ter pelo menos um administrador")

    membership.position = new_position
    session.commit()
    session.refresh(membership)
    return membership
