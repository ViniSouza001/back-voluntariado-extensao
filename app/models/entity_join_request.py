from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class JoinRequestStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELED = "canceled"


class EntityJoinRequest(Base):
    __tablename__ = "entity_join_requests"
    __table_args__ = (
        Index("ix_entity_join_requests_entity_status", "entity_id", "status"),
        Index(
            "uq_entity_join_request_pending",
            "user_id",
            "entity_id",
            unique=True,
            sqlite_where=text("status = 'pending'"),
            postgresql_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    entity_id: Mapped[int] = mapped_column(
        ForeignKey("entities.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[JoinRequestStatus] = mapped_column(
        SqlEnum(
            JoinRequestStatus,
            name="join_request_status",
            native_enum=False,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
        default=JoinRequestStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utc_now
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=False))
    reviewed_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    user = relationship("User", foreign_keys=[user_id], back_populates="join_requests")
    entity = relationship("Entity", back_populates="join_requests")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
