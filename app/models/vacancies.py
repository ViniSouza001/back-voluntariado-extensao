from datetime import date, datetime, UTC

from sqlalchemy import Boolean, Date, String, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from enum import StrEnum

from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(UTC)

class VacancyModality(StrEnum):
    REMOTE = "remote"
    IN_PERSON = "in_person"
    HYBRID = "hybrid"


class Vacancies(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    id_entity: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    address: Mapped[str] = mapped_column(String(255), nullable=True)
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utc_now)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    branch: Mapped[str] = mapped_column(String(50), nullable=False)

    modality: Mapped[VacancyModality]
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)