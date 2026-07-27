from enum import StrEnum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class MemberRole(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    MEMBER = "member"


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    __table_args__ = (
        Index("uq_member_user_organization", "user_id", "organization_id", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    role: Mapped[MemberRole] = mapped_column(
        SqlEnum(
            MemberRole,
            name="member_role",
            native_enum=False,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
        default=MemberRole.MEMBER,
    )

    user = relationship("User", back_populates="organization_memberships")
    organization = relationship("Organization", back_populates="members")
