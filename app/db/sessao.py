from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.configuracao import obter_configuracoes

configuracoes = obter_configuracoes()
eh_sqlite = configuracoes.url_banco.startswith("sqlite")
motor = create_engine(
    configuracoes.url_banco,
    connect_args={"check_same_thread": False} if eh_sqlite else {},
)
FabricaSessoes = sessionmaker(bind=motor, autoflush=False, expire_on_commit=False)


if eh_sqlite:

    @event.listens_for(Engine, "connect")
    def habilitar_chaves_estrangeiras_sqlite(conexao_dbapi, _registro_conexao) -> None:
        cursor = conexao_dbapi.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def obter_sessao() -> Generator[Session, None, None]:
    sessao = FabricaSessoes()
    try:
        yield sessao
    finally:
        sessao.close()
