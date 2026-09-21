from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class VacancyParticipant(Base):
    __tablename__ = "vacancy_participants"
    __table_args__ = (
        UniqueConstraint(
            "id_vacancy",
            "id_user",
            name="uq_vacancy_participant",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_vacancy: Mapped[int] = mapped_column(
        ForeignKey("vacancies.id", ondelete="CASCADE"), nullable=False
    )
    id_user: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), nullable=False, default=utc_now
    )

    vacancy = relationship("Vacancies", back_populates="participants")
    user = relationship("User", back_populates="vacancy_participations")
