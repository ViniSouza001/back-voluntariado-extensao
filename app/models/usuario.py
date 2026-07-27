from datetime import date

from sqlalchemy import Boolean, Date, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cpf: Mapped[str] = mapped_column(String(11), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String, nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    email_confirmado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    administrador_sistema: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )
    url_foto_perfil: Mapped[str | None] = mapped_column(String, nullable=True)

    vinculos_entidades = relationship(
        "MembroEntidade", back_populates="usuario", cascade="all, delete-orphan"
    )
    confirmacoes_email = relationship(
        "ConfirmacaoEmail", back_populates="usuario", cascade="all, delete-orphan"
    )
