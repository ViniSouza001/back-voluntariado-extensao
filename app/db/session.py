from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_configurations

configurations = get_configurations()
is_sqlite = configurations.url_database.startswith("sqlite") # verifica se o banco é sqlite
engine = create_engine (
    configurations.url_database,
    connect_args={"check_same_thread": False} if is_sqlite else {}
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

if is_sqlite:
    @event.listens_for(Engine, "connect")
    def enable_foreign_key_sqlite(connection_dbapi, _connection_record) -> None:
        cursor = connection_dbapi.cursor()
        cursor.execute("PRAGMA foreign_keys=ON") # precisa ativar para ele ler as chaves estrangeiras
        cursor.close()

def get_session() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()