from sqlalchemy import Column, String, Integer, Boolean, Float, ForeignKey, TIMESTAMP, Date, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import relationship
from datetime import date

from database.database import Base

class Entidade(Base):
    __tablename__ = "entidades"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    nome_usuario = Column("nome_usuario", String, nullable=False, unique=True)
    ramo = Column("ramo", String, nullable=False)
    descricao = Column("descricao", String, nullable=False)
    cidade = Column("cidade", String, nullable=False)
    uf = Column("uf", String, nullable=False)
    criado_em = Column("criado_em", Date, nullable=False, default=date.today())

    membros_entidade = relationship (
        "MembroEntidade",
        back_populates="entidade",
        cascade="all, delete-orphan"
    )

    def __init__(self, nome, nome_usuario, ramo, descricao, cidade, uf):
        self.nome = nome
        self.nome_usuario = nome_usuario
        self.ramo = ramo
        self.descricao = descricao
        self.cidade = cidade
        self.uf = uf
        self.criado_em = date.today()