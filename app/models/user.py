from datetime import date, datetime, UTC

from sqlalchemy import Boolean, Date, String, text, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    confirmed_email: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    
    admin_system: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )

    entity_bindings = relationship(
        "MemberEntity", back_populates="user", cascade="all, delete-orphan"
    )

    email_confirmation = relationship(
        "EmailConfirmation", back_populates="user", cascade="all, delete-orphan"
    )

    vacancy_participations = relationship(
        "VacancyParticipant", back_populates="user", cascade="all, delete-orphan"
    )

    notifications_received = relationship(
        "Notification",
        foreign_keys="Notification.recipient_id",
        back_populates="recipient",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    notifications_triggered = relationship(
        "Notification",
        foreign_keys="Notification.actor_id",
        back_populates="actor",
        passive_deletes=True,
    )
