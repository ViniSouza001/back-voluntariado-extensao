"""Refactor database schema to consistent English names.

Revision ID: 20260727_english
Revises: 9c6adc0f5c48
Create Date: 2026-07-27
"""

import hashlib
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "20260727_english"
down_revision: str | None = "9c6adc0f5c48"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.rename_table("usuarios", "users")
    op.rename_table("entidades", "organizations")
    op.rename_table("membros_entidade", "organization_members")
    op.rename_table("confirmacoes_email", "email_confirmations")

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "nome", new_column_name="name", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "senha",
            new_column_name="password_hash",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "data_nasc",
            new_column_name="birth_date",
            existing_type=sa.Date(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "cidade", new_column_name="city", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "uf", new_column_name="state", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "confirmado",
            new_column_name="is_email_confirmed",
            existing_type=sa.Boolean(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "admin",
            new_column_name="is_system_admin",
            existing_type=sa.Boolean(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "foto_perfil",
            new_column_name="profile_picture_url",
            existing_type=sa.String(),
            existing_nullable=True,
        )

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.alter_column(
            "nome", new_column_name="name", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "nome_usuario",
            new_column_name="username",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "ramo", new_column_name="sector", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "descricao",
            new_column_name="description",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "cidade", new_column_name="city", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "uf", new_column_name="state", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "criado_em",
            new_column_name="created_at",
            existing_type=sa.Date(),
            existing_nullable=False,
        )

    with op.batch_alter_table("organization_members") as batch_op:
        batch_op.alter_column(
            "id_usuario",
            new_column_name="user_id",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "id_entidade",
            new_column_name="organization_id",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "cargo",
            new_column_name="role",
            existing_type=sa.String(length=6),
            existing_nullable=False,
        )

    with op.batch_alter_table("email_confirmations") as batch_op:
        batch_op.alter_column(
            "id_usuario",
            new_column_name="user_id",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "token",
            new_column_name="token_hash",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "criado_em",
            new_column_name="created_at",
            existing_type=sa.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "expiracao",
            new_column_name="expires_at",
            existing_type=sa.TIMESTAMP(),
            existing_nullable=False,
        )

    connection = op.get_bind()
    confirmations = connection.execute(
        sa.text("SELECT id, token_hash FROM email_confirmations")
    ).mappings()
    for confirmation in confirmations:
        token_hash = hashlib.sha256(confirmation["token_hash"].encode("utf-8")).hexdigest()
        connection.execute(
            sa.text("UPDATE email_confirmations SET token_hash = :token_hash WHERE id = :id"),
            {"token_hash": token_hash, "id": confirmation["id"]},
        )

    connection.execute(
        sa.text("UPDATE organization_members SET role = 'member' WHERE role = 'membro'")
    )
    op.create_index("ix_users_cpf", "users", ["cpf"], unique=False)
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_organizations_username", "organizations", ["username"], unique=False)
    op.create_index(
        "ix_email_confirmations_token_hash", "email_confirmations", ["token_hash"], unique=True
    )


def downgrade() -> None:
    op.drop_index("ix_email_confirmations_token_hash", table_name="email_confirmations")
    op.drop_index("ix_organizations_username", table_name="organizations")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_cpf", table_name="users")

    connection = op.get_bind()
    connection.execute(
        sa.text("UPDATE organization_members SET role = 'membro' WHERE role = 'member'")
    )

    with op.batch_alter_table("email_confirmations") as batch_op:
        batch_op.alter_column(
            "user_id",
            new_column_name="id_usuario",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "token_hash",
            new_column_name="token",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "created_at",
            new_column_name="criado_em",
            existing_type=sa.TIMESTAMP(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "expires_at",
            new_column_name="expiracao",
            existing_type=sa.TIMESTAMP(),
            existing_nullable=False,
        )

    with op.batch_alter_table("organization_members") as batch_op:
        batch_op.alter_column(
            "user_id",
            new_column_name="id_usuario",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "organization_id",
            new_column_name="id_entidade",
            existing_type=sa.Integer(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "role",
            new_column_name="cargo",
            existing_type=sa.String(length=6),
            existing_nullable=False,
        )

    with op.batch_alter_table("organizations") as batch_op:
        batch_op.alter_column(
            "name", new_column_name="nome", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "username",
            new_column_name="nome_usuario",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "sector", new_column_name="ramo", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "description",
            new_column_name="descricao",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "city", new_column_name="cidade", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "state", new_column_name="uf", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "created_at",
            new_column_name="criado_em",
            existing_type=sa.Date(),
            existing_nullable=False,
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "name", new_column_name="nome", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "password_hash",
            new_column_name="senha",
            existing_type=sa.String(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "birth_date",
            new_column_name="data_nasc",
            existing_type=sa.Date(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "city", new_column_name="cidade", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "state", new_column_name="uf", existing_type=sa.String(), existing_nullable=False
        )
        batch_op.alter_column(
            "is_email_confirmed",
            new_column_name="confirmado",
            existing_type=sa.Boolean(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "is_system_admin",
            new_column_name="admin",
            existing_type=sa.Boolean(),
            existing_nullable=False,
        )
        batch_op.alter_column(
            "profile_picture_url",
            new_column_name="foto_perfil",
            existing_type=sa.String(),
            existing_nullable=True,
        )

    op.rename_table("email_confirmations", "confirmacoes_email")
    op.rename_table("organization_members", "membros_entidade")
    op.rename_table("organizations", "entidades")
    op.rename_table("users", "usuarios")
