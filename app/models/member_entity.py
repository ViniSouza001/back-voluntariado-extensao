from enum import StrEnum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class MemberPosition(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    MEMBER = "member"

class MemberEntity(Base):
    __tablename__ = "members_entities"
    __table_args__ = (
        Index("uq_member_user_entity", "id_user", "id_entity", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    id_entity: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    position: Mapped[MemberPosition] = mapped_column(
        SqlEnum(
            MemberPosition,
            name="member_position",
            native_enum=False,
            values_callable=lambda enum_class: [member.value for member in enum_class]
        ),
        nullable=False,
        default=MemberPosition.MEMBER
    )

    user = relationship("User", back_populates="entity_bindings")
    entity = relationship("Entity", back_populates="members")


    # fazer o arquivo models.entity.py
    