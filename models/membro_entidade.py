from sqlalchemy import Column, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from database.database import Base

class CargoMembro(str, PyEnum):
    admin = "admin"
    editor = "editor"
    membro = "membro"

class MembroEntidade(Base):
    __tablename__ = "membros_entidade"

    id = Column(Integer, primary_key=True, autoincrement=True)

    id_usuario = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    id_entidade = Column(Integer, ForeignKey("entidades.id"), nullable=False)

    cargo = Column(Enum(CargoMembro), nullable=False, default=CargoMembro.membro)

    usuario = relationship("Usuario", back_populates="membros_entidade")
    entidade = relationship("Entidade", back_populates="membros_entidade")