from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, TIMESTAMP, Date, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship

from database.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    cpf = Column("cpf", String(11), nullable=False, unique=True)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    data_nasc = Column("data_nasc", Date, nullable=False)
    cidade = Column("cidade", String, nullable=False)
    uf = Column("uf", String, nullable=False)
    confirmado = Column("confirmado", Boolean, nullable=False)
    admin = Column("admin", Boolean, nullable=False)
    foto_perfil = Column("foto_perfil", String, nullable=True)

    membros_entidade = relationship (
        "MembroEntidade",
        back_populates="usuario",
        cascade="all, delete-orphan"
    )

    def __init__(self, nome, cpf, email, senha, data_nasc, cidade, uf):
        self.nome = nome
        self.cpf = cpf
        self.email = email
        self.senha = senha
        self.data_nasc = data_nasc
        self.cidade = cidade
        self.uf = uf
        self.confirmado = False
        self.admin = False
