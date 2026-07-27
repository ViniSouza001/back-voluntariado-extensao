from datetime import date

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Entidade(Base):
    __tablename__ = "entidades"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    nome_usuario: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    setor: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[str] = mapped_column(String, nullable=False)
    cidade: Mapped[str] = mapped_column(String(100), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    criado_em: Mapped[date] = mapped_column(Date, nullable=False, default=date.today)

    membros = relationship(
        "MembroEntidade", back_populates="entidade", cascade="all, delete-orphan"
    )
