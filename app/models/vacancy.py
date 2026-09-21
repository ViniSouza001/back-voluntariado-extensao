from datetime import date, datetime, UTC

from sqlalchemy import Boolean, Date, String, TIMESTAMP, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from enum import StrEnum

from app.db.base import Base

def utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)

class VacancyModality(StrEnum):
    REMOTE = "remote"
    IN_PERSON = "in_person"

class VacancyBranch(StrEnum):
    ANIMALS = "animals"
    ENVIRONMENT = "environment"
    EDUCATION = "education"
    HEALTH = "health"
    SOCIAL_ASSISTANCE = "social_assistance"
    ELDERLY = "elderly"
    CHILDREN_AND_TEENS = "children_and_teens"
    INCLUSION = "inclusion"
    CULTURE_AND_ART = "culture_and_art"
    SPORTS = "sports"
    TECHNOLOGY = "technology"
    HUMANITARIAN_AID = "humanitarian_aid"
    COMMUNITY = "community"
    EVENTS = "events"


class Vacancies(Base):
    __tablename__ = "vacancies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    id_entity: Mapped[int] = mapped_column(ForeignKey("entities.id"), nullable=False)
    # Datas guardadas em UTC, sem informação de fuso na coluna.
    posted_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False, default=utc_now)
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    branch: Mapped[VacancyBranch]

    modality: Mapped[VacancyModality]

    cep: Mapped[str | None] = mapped_column(String(8), nullable=True)
    number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    thoroughfare: Mapped[str | None] = mapped_column(String(100), nullable=True)
    details: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    uf: Mapped[str | None] = mapped_column(String(2), nullable=True)

    participants = relationship(
        "VacancyParticipant",
        back_populates="vacancy",
        cascade="all, delete-orphan",
    )

    notifications = relationship(
        "Notification", back_populates="vacancy", passive_deletes=True
    )
