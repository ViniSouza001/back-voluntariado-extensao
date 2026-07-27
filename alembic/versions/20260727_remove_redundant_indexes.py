"""Remove indexes duplicated by unique constraints.

Revision ID: 20260727_indexes
Revises: 20260727_membership
Create Date: 2026-07-27
"""

from collections.abc import Sequence

from alembic import op

revision: str = "20260727_indexes"
down_revision: str | None = "20260727_membership"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index("ix_users_cpf", table_name="users")
    op.drop_index("ix_organizations_username", table_name="organizations")


def downgrade() -> None:
    op.create_index("ix_organizations_username", "organizations", ["username"], unique=False)
    op.create_index("ix_users_cpf", "users", ["cpf"], unique=False)
