from sqlalchemy.orm import Session

from app.core.excecoes import ErroAutenticacao, ErroValidacao
from app.core.seguranca import gerar_hash_senha, verificar_senha
from app.models.usuario import Usuario
from app.schemas.usuario import AlteracaoSenha, AtualizacaoUsuario


class ServicoUsuario:
    def __init__(self, sessao: Session):
        self.sessao = sessao

    def atualizar(self, usuario: Usuario, dados: AtualizacaoUsuario) -> Usuario:
        alteracoes = dados.model_dump(exclude_unset=True)
        if "uf" in alteracoes and alteracoes["uf"] is not None:
            alteracoes["uf"] = alteracoes["uf"].upper()
        for nome_campo, valor in alteracoes.items():
            setattr(usuario, nome_campo, valor.strip() if isinstance(valor, str) else valor)
        self.sessao.commit()
        self.sessao.refresh(usuario)
        return usuario

    def alterar_senha(self, usuario: Usuario, dados: AlteracaoSenha) -> None:
        if not verificar_senha(dados.senha_atual, usuario.senha_hash):
            raise ErroAutenticacao("A senha atual está incorreta")
        if dados.nova_senha != dados.confirmacao_nova_senha:
            raise ErroValidacao("As novas senhas não coincidem")
        if verificar_senha(dados.nova_senha, usuario.senha_hash):
            raise ErroValidacao("A nova senha deve ser diferente da senha atual")
        try:
            usuario.senha_hash = gerar_hash_senha(dados.nova_senha)
        except ValueError as erro:
            raise ErroValidacao(str(erro)) from erro
        self.sessao.commit()

    def excluir(self, usuario: Usuario) -> None:
        self.sessao.delete(usuario)
        self.sessao.commit()
