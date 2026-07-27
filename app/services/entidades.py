from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.excecoes import ErroConflito
from app.models.entidade import Entidade
from app.models.membro_entidade import CargoMembro, MembroEntidade
from app.models.usuario import Usuario
from app.repositories.entidades import RepositorioEntidade
from app.schemas.entidade import CriacaoEntidade


class ServicoEntidade:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def criar(self, dados: CriacaoEntidade, criador: Usuario) -> Entidade:
        nome_usuario = dados.nome_usuario.lower()
        if RepositorioEntidade.buscar_por_nome_usuario(self.sessao, nome_usuario):
            raise ErroConflito("Já existe uma entidade com este nome de usuário")

        entidade = Entidade(
            nome=dados.nome.strip(),
            nome_usuario=nome_usuario,
            setor=dados.setor.strip(),
            descricao=dados.descricao.strip(),
            cidade=dados.cidade.strip(),
            uf=dados.uf.upper(),
        )
        try:
            RepositorioEntidade.adicionar(self.sessao, entidade)
            self.sessao.flush()
            self.sessao.add(
                MembroEntidade(
                    id_usuario=criador.id,
                    id_entidade=entidade.id,
                    cargo=CargoMembro.ADMIN,
                )
            )
            self.sessao.commit()
            self.sessao.refresh(entidade)
        except IntegrityError as erro:
            self.sessao.rollback()
            raise ErroConflito("O nome de usuário da entidade já está em uso") from erro
        except Exception:
            self.sessao.rollback()
            raise
        return entidade
