from sqlalchemy import Date, String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enum import StrEnum
from datetime import datetime, UTC

from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(UTC)

# classe de status (pendente, aceito, recusado)
class InvitationStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

# classe de tipo de convite (entidade, vaga, amizade)
class InvitationType(StrEnum):
    ENTITY = "entity"
    VACANCY = "vacancy"
    FRIEND = "friend"

class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(default=InvitationStatus.PENDING, nullable=False)
    invitation_type: Mapped[InvitationType]
    target_id: Mapped[int | None]
    recipient_read_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    sender_archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )
    recipient_archived_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=False), nullable=True
    )

    sender = relationship(
        "User", foreign_keys=[sender_id]
    )

    recipient = relationship(
        "User", foreign_keys=[recipient_id]
    )

    notifications = relationship(
        "Notification", back_populates="invitation", passive_deletes=True
    )
