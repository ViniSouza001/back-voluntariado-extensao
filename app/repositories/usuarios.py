from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.usuario import Usuario


class RepositorioUsuario:
    @staticmethod
    def buscar_por_id(sessao: Session, id_usuario: int) -> Usuario | None:
        return sessao.scalar(select(Usuario).where(Usuario.id == id_usuario))

    @staticmethod
    def buscar_por_email(sessao: Session, email: str) -> Usuario | None:
        return sessao.scalar(select(Usuario).where(Usuario.email == email.lower()))

    @staticmethod
    def buscar_por_cpf(sessao: Session, cpf: str) -> Usuario | None:
        return sessao.scalar(select(Usuario).where(Usuario.cpf == cpf))

    @staticmethod
    def adicionar(sessao: Session, usuario: Usuario) -> Usuario:
        sessao.add(usuario)
        return usuario
