"""Remove invitation read state.

Revision ID: b7d4c92e1a60
Revises: 91f0a6d2c8b4
"""

from alembic import op
import sqlalchemy as sa


revision = "b7d4c92e1a60"
down_revision = "91f0a6d2c8b4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.drop_column("recipient_read_at")


def downgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.add_column(
            sa.Column("recipient_read_at", sa.DateTime(), nullable=True)
        )
