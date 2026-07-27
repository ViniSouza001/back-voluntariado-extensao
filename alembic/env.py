from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

import app.models  # noqa: F401 -- registra os metadados dos modelos
from alembic import context
from app.db.base import Base

# Configuração do Alembic com acesso aos valores do arquivo .ini.
configuracao = context.config

# Configura os logs definidos no arquivo do Alembic.
if configuracao.config_file_name is not None:
    fileConfig(configuracao.config_file_name)

metadados_alvo = Base.metadata


def executar_migracoes_offline() -> None:
    """Executa as migrações sem abrir uma conexão com o banco."""
    url = configuracao.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=metadados_alvo,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def executar_migracoes_online() -> None:
    """Executa as migrações utilizando uma conexão com o banco."""
    motor = engine_from_config(
        configuracao.get_section(configuracao.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with motor.connect() as conexao:
        context.configure(
            connection=conexao,
            target_metadata=metadados_alvo,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    executar_migracoes_offline()
else:
    executar_migracoes_online()
