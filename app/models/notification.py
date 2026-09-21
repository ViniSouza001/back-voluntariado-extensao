from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SqlEnum,
    ForeignKey,
    Index,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class NotificationType(StrEnum):
    INVITATION_RECEIVED = "invitation_received"
    INVITATION_ACCEPTED = "invitation_accepted"
    INVITATION_REJECTED = "invitation_rejected"
    ENTITY_MEMBER_JOINED = "entity_member_joined"
    ENTITY_MEMBER_LEFT = "entity_member_left"
    ENTITY_ROLE_CHANGED = "entity_role_changed"
    ENTITY_MEMBER_REMOVED = "entity_member_removed"
    VACANCY_CREATED = "vacancy_created"
    VACANCY_UPDATED = "vacancy_updated"
    VACANCY_DELETED = "vacancy_deleted"
    VACANCY_PARTICIPANT_JOINED = "vacancy_participant_joined"
    VACANCY_PARTICIPANT_LEFT = "vacancy_participant_left"
    VACANCY_PARTICIPANT_REMOVED = "vacancy_participant_removed"


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (
        CheckConstraint(
            "(invitation_id IS NULL OR entity_id IS NULL) AND "
            "(invitation_id IS NULL OR vacancy_id IS NULL) AND "
            "(entity_id IS NULL OR vacancy_id IS NULL)",
            name="ck_notification_single_resource",
        ),
        Index(
            "ix_notifications_recipient_archived_created",
            "recipient_id",
            "archived_at",
            "created_at",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipient_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    notification_type: Mapped[NotificationType] = mapped_column(
        SqlEnum(
            NotificationType,
            name="notification_type",
            native_enum=False,
            values_callable=lambda enum_class: [item.value for item in enum_class],
        ),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
    invitation_id: Mapped[int | None] = mapped_column(
        ForeignKey("invitations.id", ondelete="SET NULL"), nullable=True
    )
    entity_id: Mapped[int | None] = mapped_column(
        ForeignKey("entities.id", ondelete="SET NULL"), nullable=True
    )
    vacancy_id: Mapped[int | None] = mapped_column(
        ForeignKey("vacancies.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utc_now
    )
    read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    recipient = relationship(
        "User",
        foreign_keys=[recipient_id],
        back_populates="notifications_received",
    )
    actor = relationship(
        "User",
        foreign_keys=[actor_id],
        back_populates="notifications_triggered",
    )
    invitation = relationship("Invitation", back_populates="notifications")
    entity = relationship("Entity", back_populates="notifications")
    vacancy = relationship("Vacancies", back_populates="notifications")
