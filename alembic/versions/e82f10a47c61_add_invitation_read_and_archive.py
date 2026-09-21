"""Add invitation read and archive fields.

Revision ID: e82f10a47c61
Revises: c4a91f6d28b3
"""

from alembic import op
import sqlalchemy as sa


revision = "e82f10a47c61"
down_revision = "c4a91f6d28b3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.add_column(
            sa.Column("recipient_read_at", sa.DateTime(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("sender_archived_at", sa.DateTime(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("recipient_archived_at", sa.DateTime(), nullable=True)
        )


def downgrade() -> None:
    with op.batch_alter_table("invitations") as batch_op:
        batch_op.drop_column("recipient_archived_at")
        batch_op.drop_column("sender_archived_at")
        batch_op.drop_column("recipient_read_at")
