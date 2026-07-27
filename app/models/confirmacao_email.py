from datetime import UTC, datetime

from sqlalchemy import TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ConfirmacaoEmail(Base):
    __tablename__ = "confirmacoes_email"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    hash_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    expira_em: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    usuario = relationship("Usuario", back_populates="confirmacoes_email")
