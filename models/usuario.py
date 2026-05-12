from sqlalchemy import create_engine, Column, String, Integer, Boolean, Float, ForeignKey, TIMESTAMP, Date, Enum
from enum import Enum as PyEnum
from sqlalchemy.orm import declarative_base, relationship

from database.database import Base

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    nome = Column("nome", String, nullable=False)
    email = Column("email", String, nullable=False)
    senha = Column("senha", String, nullable=False)
    data_nasc = Column("data_nasc", Date, nullable=False)
    cidade = Column("cidade", String, nullable=False)
    uf = Column("uf", String, nullable=False)
    confirmado = Column("Confirmado", Boolean, nullable=False)
    admin = Column("admin", Boolean, nullable=False)

    def __init__(self, nome, email, senha, data_nasc, cidade, uf, confirmado, admin=False):
        self.nome = nome
        self.email = email
        self.senha = senha
        self.data_nasc = data_nasc
        self.cidade = cidade
        self.uf = uf
        self.confirmado = confirmado
        self.admin = admin
