"""Add requests to participate in a vacancy.

Revision ID: c0e1a2b3d4f5
Revises: b6f2e0a9c431
"""

from alembic import op
import sqlalchemy as sa


revision = "c0e1a2b3d4f5"
down_revision = "b6f2e0a9c431"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vacancy_join_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("vacancy_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "accepted", "rejected", "canceled",
                name="vacancy_join_request_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("reviewed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["vacancy_id"], ["vacancies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reviewed_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_vacancy_join_request_pending",
        "vacancy_join_requests",
        ["user_id", "vacancy_id"],
        unique=True,
        sqlite_where=sa.text("status = 'pending'"),
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_index(
        "ix_vacancy_join_requests_vacancy_status",
        "vacancy_join_requests", ["vacancy_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_vacancy_join_requests_vacancy_status", table_name="vacancy_join_requests"
    )
    op.drop_index(
        "uq_vacancy_join_request_pending", table_name="vacancy_join_requests"
    )
    op.drop_table("vacancy_join_requests")
