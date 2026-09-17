"""Allow a user to belong to only one entity.

Revision ID: d7c81a4e69b2
Revises: 5c3a37e8d380
"""
from alembic import op
import sqlalchemy as sa

revision = "d7c81a4e69b2"
down_revision = "5c3a37e8d380"
branch_labels = None
depends_on = None


def upgrade() -> None:
    connection = op.get_bind()
    duplicate = connection.execute(sa.text(
        "SELECT id_user FROM members_entities "
        "GROUP BY id_user HAVING COUNT(*) > 1 LIMIT 1"
    )).scalar()
    if duplicate is not None:
        raise RuntimeError(
            "Há usuários ligados a mais de uma entidade. "
            "Resolva esses vínculos antes de aplicar esta migração."
        )
    op.create_index(
        "uq_member_one_entity_per_user", "members_entities", ["id_user"], unique=True
    )


def downgrade() -> None:
    op.drop_index("uq_member_one_entity_per_user", table_name="members_entities")
