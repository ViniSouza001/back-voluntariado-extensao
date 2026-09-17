from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.member_entity import MemberEntity, MemberPosition


def count_entity_admins(session: Session, id_entity: int) -> int:
    return session.scalar(
        select(func.count()).select_from(MemberEntity).where(
            MemberEntity.id_entity == id_entity,
            MemberEntity.position == MemberPosition.ADMIN,
        )
    )
