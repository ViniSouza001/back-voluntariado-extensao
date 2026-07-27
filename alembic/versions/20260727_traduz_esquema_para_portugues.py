"""Traduz o esquema atual do banco de dados para português.

Revision ID: 20260727_portugues
Revises: 20260727_indexes
Create Date: 2026-07-27
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260727_portugues"
down_revision: str | None = "20260727_indexes"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_email_confirmations_token_hash", table_name="email_confirmations")
    op.drop_index("uq_member_user_organization", table_name="organization_members")

    op.rename_table("users", "usuarios")
    op.rename_table("organizations", "entidades")
    op.rename_table("organization_members", "membros_entidade")
    op.rename_table("email_confirmations", "confirmacoes_email")

    with op.batch_alter_table("usuarios") as alteracao:
        alteracao.alter_column(
            "name", new_column_name="nome", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "password_hash",
            new_column_name="senha_hash",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "birth_date",
            new_column_name="data_nascimento",
            existing_type=sa.Date(),
            nullable=False,
        )
        alteracao.alter_column(
            "city", new_column_name="cidade", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "state", new_column_name="uf", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "is_email_confirmed",
            new_column_name="email_confirmado",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        alteracao.alter_column(
            "is_system_admin",
            new_column_name="administrador_sistema",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        alteracao.alter_column(
            "profile_picture_url",
            new_column_name="url_foto_perfil",
            existing_type=sa.String(),
            nullable=True,
        )

    with op.batch_alter_table("entidades") as alteracao:
        alteracao.alter_column(
            "name", new_column_name="nome", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "username",
            new_column_name="nome_usuario",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "sector", new_column_name="setor", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "description",
            new_column_name="descricao",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "city", new_column_name="cidade", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "state", new_column_name="uf", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "created_at",
            new_column_name="criado_em",
            existing_type=sa.Date(),
            nullable=False,
        )

    with op.batch_alter_table("membros_entidade") as alteracao:
        alteracao.alter_column(
            "user_id",
            new_column_name="id_usuario",
            existing_type=sa.Integer(),
            nullable=False,
        )
        alteracao.alter_column(
            "organization_id",
            new_column_name="id_entidade",
            existing_type=sa.Integer(),
            nullable=False,
        )
        alteracao.alter_column(
            "role", new_column_name="cargo", existing_type=sa.String(6), nullable=False
        )

    with op.batch_alter_table("confirmacoes_email") as alteracao:
        alteracao.alter_column(
            "user_id",
            new_column_name="id_usuario",
            existing_type=sa.Integer(),
            nullable=False,
        )
        alteracao.alter_column(
            "token_hash",
            new_column_name="hash_token",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "created_at",
            new_column_name="criado_em",
            existing_type=sa.TIMESTAMP(),
            nullable=False,
        )
        alteracao.alter_column(
            "expires_at",
            new_column_name="expira_em",
            existing_type=sa.TIMESTAMP(),
            nullable=False,
        )

    conexao = op.get_bind()
    conexao.execute(sa.text("UPDATE membros_entidade SET cargo = 'membro' WHERE cargo = 'member'"))

    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index(
        "ix_confirmacoes_email_hash_token",
        "confirmacoes_email",
        ["hash_token"],
        unique=True,
    )
    op.create_index(
        "uq_membro_usuario_entidade",
        "membros_entidade",
        ["id_usuario", "id_entidade"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_membro_usuario_entidade", table_name="membros_entidade")
    op.drop_index("ix_confirmacoes_email_hash_token", table_name="confirmacoes_email")
    op.drop_index("ix_usuarios_email", table_name="usuarios")

    conexao = op.get_bind()
    conexao.execute(sa.text("UPDATE membros_entidade SET cargo = 'member' WHERE cargo = 'membro'"))

    with op.batch_alter_table("confirmacoes_email") as alteracao:
        alteracao.alter_column(
            "id_usuario",
            new_column_name="user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        alteracao.alter_column(
            "hash_token",
            new_column_name="token_hash",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "criado_em",
            new_column_name="created_at",
            existing_type=sa.TIMESTAMP(),
            nullable=False,
        )
        alteracao.alter_column(
            "expira_em",
            new_column_name="expires_at",
            existing_type=sa.TIMESTAMP(),
            nullable=False,
        )

    with op.batch_alter_table("membros_entidade") as alteracao:
        alteracao.alter_column(
            "id_usuario",
            new_column_name="user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        alteracao.alter_column(
            "id_entidade",
            new_column_name="organization_id",
            existing_type=sa.Integer(),
            nullable=False,
        )
        alteracao.alter_column(
            "cargo", new_column_name="role", existing_type=sa.String(6), nullable=False
        )

    with op.batch_alter_table("entidades") as alteracao:
        alteracao.alter_column(
            "nome", new_column_name="name", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "nome_usuario",
            new_column_name="username",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "setor", new_column_name="sector", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "descricao",
            new_column_name="description",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "cidade", new_column_name="city", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "uf", new_column_name="state", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "criado_em",
            new_column_name="created_at",
            existing_type=sa.Date(),
            nullable=False,
        )

    with op.batch_alter_table("usuarios") as alteracao:
        alteracao.alter_column(
            "nome", new_column_name="name", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "senha_hash",
            new_column_name="password_hash",
            existing_type=sa.String(),
            nullable=False,
        )
        alteracao.alter_column(
            "data_nascimento",
            new_column_name="birth_date",
            existing_type=sa.Date(),
            nullable=False,
        )
        alteracao.alter_column(
            "cidade", new_column_name="city", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "uf", new_column_name="state", existing_type=sa.String(), nullable=False
        )
        alteracao.alter_column(
            "email_confirmado",
            new_column_name="is_email_confirmed",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        alteracao.alter_column(
            "administrador_sistema",
            new_column_name="is_system_admin",
            existing_type=sa.Boolean(),
            nullable=False,
        )
        alteracao.alter_column(
            "url_foto_perfil",
            new_column_name="profile_picture_url",
            existing_type=sa.String(),
            nullable=True,
        )

    op.rename_table("confirmacoes_email", "email_confirmations")
    op.rename_table("membros_entidade", "organization_members")
    op.rename_table("entidades", "organizations")
    op.rename_table("usuarios", "users")

    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index(
        "ix_email_confirmations_token_hash",
        "email_confirmations",
        ["token_hash"],
        unique=True,
    )
    op.create_index(
        "uq_member_user_organization",
        "organization_members",
        ["user_id", "organization_id"],
        unique=True,
    )
