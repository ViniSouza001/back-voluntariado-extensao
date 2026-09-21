"""Create vacancy participants table.

Revision ID: c4a91f6d28b3
Revises: 70562aa40200
"""

from alembic import op
import sqlalchemy as sa


revision = "c4a91f6d28b3"
down_revision = "70562aa40200"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vacancy_participants",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_vacancy", sa.Integer(), nullable=False),
        sa.Column("id_user", sa.Integer(), nullable=False),
        sa.Column("joined_at", sa.DateTime(timezone=False), nullable=False),
        sa.ForeignKeyConstraint(
            ["id_vacancy"], ["vacancies.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["id_user"], ["users.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "id_vacancy", "id_user", name="uq_vacancy_participant"
        ),
    )


def downgrade() -> None:
    op.drop_table("vacancy_participants")
