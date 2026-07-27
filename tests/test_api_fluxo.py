import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.db.sessao import obter_sessao
from app.models.confirmacao_email import ConfirmacaoEmail
from app.principal import criar_aplicacao


class TestesFluxoApi(unittest.TestCase):
    def setUp(self) -> None:
        self.diretorio_temporario = tempfile.TemporaryDirectory()
        caminho_banco = Path(self.diretorio_temporario.name) / "teste.db"
        self.motor = create_engine(
            f"sqlite:///{caminho_banco.as_posix()}",
            connect_args={"check_same_thread": False},
        )
        Base.metadata.create_all(self.motor)
        self.fabrica_sessoes = sessionmaker(
            bind=self.motor, autoflush=False, expire_on_commit=False
        )

        aplicacao = criar_aplicacao()

        def substituir_banco():
            sessao = self.fabrica_sessoes()
            try:
                yield sessao
            finally:
                sessao.close()

        aplicacao.dependency_overrides[obter_sessao] = substituir_banco
        self.contexto_cliente = TestClient(aplicacao)
        self.cliente = self.contexto_cliente.__enter__()

    def tearDown(self) -> None:
        self.contexto_cliente.__exit__(None, None, None)
        self.motor.dispose()
        self.diretorio_temporario.cleanup()

    def test_fluxo_completo_conta_e_entidade(self) -> None:
        self.assertEqual(self.cliente.get("/saude").json(), {"estado": "saudável"})

        with patch(
            "app.services.autenticacao.secrets.token_urlsafe",
            return_value="known-token",
        ):
            cadastro = self.cliente.post(
                "/api/v1/autenticacao/cadastro",
                json={
                    "nome": "Usuário de Teste",
                    "cpf": "529.982.247-25",
                    "email": "usuario@example.com",
                    "senha": "senha-segura",
                    "data_nascimento": "2000-01-01",
                    "cidade": "Campinas",
                    "uf": "sp",
                },
            )
        self.assertEqual(cadastro.status_code, 201, cadastro.text)
        self.assertFalse(cadastro.json()["email_confirmacao_enviado"])

        with self.fabrica_sessoes() as sessao:
            confirmacao = sessao.scalar(select(ConfirmacaoEmail))
            self.assertIsNotNone(confirmacao)
            self.assertNotEqual(confirmacao.hash_token, "known-token")

        entrada_sem_confirmacao = self.cliente.post(
            "/api/v1/autenticacao/entrar",
            json={"email": "usuario@example.com", "senha": "senha-segura"},
        )
        self.assertEqual(entrada_sem_confirmacao.status_code, 401)

        confirmacao = self.cliente.get("/api/v1/autenticacao/confirmar-email/known-token")
        self.assertEqual(confirmacao.status_code, 200, confirmacao.text)

        entrada = self.cliente.post(
            "/api/v1/autenticacao/entrar",
            json={"email": "usuario@example.com", "senha": "senha-segura"},
        )
        self.assertEqual(entrada.status_code, 200, entrada.text)
        cabecalhos = {"Authorization": f"Bearer {entrada.json()['token_acesso']}"}

        perfil = self.cliente.get("/api/v1/usuarios/eu", headers=cabecalhos)
        self.assertEqual(perfil.status_code, 200, perfil.text)
        self.assertEqual(perfil.json()["uf"], "SP")

        entidade = self.cliente.post(
            "/api/v1/entidades",
            headers=cabecalhos,
            json={
                "nome": "Mãos que Ajudam",
                "nome_usuario": "maos-que-ajudam",
                "setor": "Educação",
                "descricao": "Projetos voluntários de educação",
                "cidade": "Campinas",
                "uf": "sp",
            },
        )
        self.assertEqual(entidade.status_code, 201, entidade.text)
        self.assertEqual(entidade.json()["nome_usuario"], "maos-que-ajudam")

        perfil_atualizado = self.cliente.patch(
            "/api/v1/usuarios/eu",
            headers=cabecalhos,
            json={"cidade": "Sao Paulo", "uf": "sp"},
        )
        self.assertEqual(perfil_atualizado.status_code, 200, perfil_atualizado.text)
        self.assertEqual(perfil_atualizado.json()["cidade"], "Sao Paulo")

        alteracao_senha = self.cliente.patch(
            "/api/v1/usuarios/eu/senha",
            headers=cabecalhos,
            json={
                "senha_atual": "senha-segura",
                "nova_senha": "nova-senha-segura",
                "confirmacao_nova_senha": "nova-senha-segura",
            },
        )
        self.assertEqual(alteracao_senha.status_code, 200, alteracao_senha.text)

        nova_entrada = self.cliente.post(
            "/api/v1/autenticacao/entrar",
            json={"email": "usuario@example.com", "senha": "nova-senha-segura"},
        )
        self.assertEqual(nova_entrada.status_code, 200, nova_entrada.text)
        novos_cabecalhos = {"Authorization": f"Bearer {nova_entrada.json()['token_acesso']}"}

        exclusao = self.cliente.delete("/api/v1/usuarios/eu", headers=novos_cabecalhos)
        self.assertEqual(exclusao.status_code, 204, exclusao.text)
        self.assertEqual(
            self.cliente.get("/api/v1/usuarios/eu", headers=novos_cabecalhos).status_code,
            401,
        )


if __name__ == "__main__":
    unittest.main()
