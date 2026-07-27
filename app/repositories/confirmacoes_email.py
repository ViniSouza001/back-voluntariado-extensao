from sqlalchemy import delete as excluir
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.confirmacao_email import ConfirmacaoEmail


class RepositorioConfirmacaoEmail:
    @staticmethod
    def buscar_por_hash_token(sessao: Session, hash_token: str) -> ConfirmacaoEmail | None:
        return sessao.scalar(
            select(ConfirmacaoEmail).where(ConfirmacaoEmail.hash_token == hash_token)
        )

    @staticmethod
    def excluir_do_usuario(sessao: Session, id_usuario: int) -> None:
        sessao.execute(excluir(ConfirmacaoEmail).where(ConfirmacaoEmail.id_usuario == id_usuario))
