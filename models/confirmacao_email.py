from sqlalchemy import Column, String, Integer, ForeignKey, TIMESTAMP
from datetime import datetime
from database.database import Base

class ConfirmacaoEmail(Base):
    __tablename__ = "confirmacoes_email"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    id_usuario = Column("id_usuario", Integer, ForeignKey("usuarios.id"), nullable=False)
    token = Column("token", String, nullable=False)
    criado_em = Column("criado_em", TIMESTAMP, default=datetime.now, nullable=False)
    expiracao = Column("expiracao", TIMESTAMP, nullable=False)

    def __init__(self, id_usuario, token, criado_em, expiracao):
        self.id_usuario = id_usuario
        self.token = token
        self.criado_em = criado_em
        self.expiracao = expiracao