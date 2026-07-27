"""Adiciona o índice único de vínculo entre usuário e entidade.

Revision ID: 20260727_membership
Revises: 20260727_english
Create Date: 2026-07-27
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260727_membership"
down_revision: str | None = "20260727_english"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_index(
        "uq_member_user_organization",
        "organization_members",
        ["user_id", "organization_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_member_user_organization", table_name="organization_members")
