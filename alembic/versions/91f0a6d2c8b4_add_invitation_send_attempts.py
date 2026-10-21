"""Add invitation send attempts for cooldown enforcement.

Revision ID: 91f0a6d2c8b4
Revises: 6438217e9e2d
"""

from alembic import op
import sqlalchemy as sa


revision = "91f0a6d2c8b4"
down_revision = "6438217e9e2d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "invitation_send_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("attempted_at", sa.DateTime(timezone=False), nullable=False),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_invitation_send_attempts_sender_attempted",
        "invitation_send_attempts",
        ["sender_id", "attempted_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_invitation_send_attempts_sender_attempted",
        table_name="invitation_send_attempts",
    )
    op.drop_table("invitation_send_attempts")
