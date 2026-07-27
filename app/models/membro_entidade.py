from enum import StrEnum

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class CargoMembro(StrEnum):
    ADMIN = "admin"
    EDITOR = "editor"
    MEMBRO = "membro"


class MembroEntidade(Base):
    __tablename__ = "membros_entidade"
    __table_args__ = (
        Index("uq_membro_usuario_entidade", "id_usuario", "id_entidade", unique=True),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_usuario: Mapped[int] = mapped_column(ForeignKey("usuarios.id"), nullable=False)
    id_entidade: Mapped[int] = mapped_column(ForeignKey("entidades.id"), nullable=False)
    cargo: Mapped[CargoMembro] = mapped_column(
        SqlEnum(
            CargoMembro,
            name="cargo_membro",
            native_enum=False,
            values_callable=lambda classe_enum: [membro.value for membro in classe_enum],
        ),
        nullable=False,
        default=CargoMembro.MEMBRO,
    )

    usuario = relationship("Usuario", back_populates="vinculos_entidades")
    entidade = relationship("Entidade", back_populates="membros")
