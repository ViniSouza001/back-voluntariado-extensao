from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.entity_join_request import JoinRequestStatus


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class VacancyJoinRequest(Base):
    __tablename__ = "vacancy_join_requests"
    __table_args__ = (
        Index("ix_vacancy_join_requests_vacancy_status", "vacancy_id", "status"),
        Index(
            "uq_vacancy_join_request_pending",
            "user_id",
            "vacancy_id",
            unique=True,
            sqlite_where=text("status = 'pending'"),
            postgresql_where=text("status = 'pending'"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    vacancy_id: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False
    )
    status: Mapped[JoinRequestStatus] = mapped_column(
        SqlEnum(
            JoinRequestStatus,
            name="vacancy_join_request_status",
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

    user = relationship("User", foreign_keys=[user_id], back_populates="vacancy_join_requests")
    vacancy = relationship("Vacancies", back_populates="join_requests")
    reviewed_by = relationship("User", foreign_keys=[reviewed_by_id])
