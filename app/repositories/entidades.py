from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entidade import Entidade


class RepositorioEntidade:
    @staticmethod
    def buscar_por_nome_usuario(sessao: Session, nome_usuario: str) -> Entidade | None:
        return sessao.scalar(select(Entidade).where(Entidade.nome_usuario == nome_usuario.lower()))

    @staticmethod
    def adicionar(sessao: Session, entidade: Entidade) -> Entidade:
        sessao.add(entidade)
        return entidade
