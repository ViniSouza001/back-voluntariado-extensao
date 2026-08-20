from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def current_date() -> datetime:
    return datetime.now(UTC)


class EmailConfirmation(Base):
    __tablename__ = "email_confirmations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    hash_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=current_date
    )
    expire_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    resend_at: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    user = relationship("User", back_populates="email_confirmation")
