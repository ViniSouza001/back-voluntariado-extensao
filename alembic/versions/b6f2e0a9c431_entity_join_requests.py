"""Add requests to join an entity.

Revision ID: b6f2e0a9c431
Revises: a13d86c29f04
"""

from alembic import op
import sqlalchemy as sa


revision = "b6f2e0a9c431"
down_revision = "a13d86c29f04"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "entity_join_requests",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "pending", "accepted", "rejected", "canceled",
                name="join_request_status", native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("reviewed_by_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["entity_id"], ["entities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["reviewed_by_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_entity_join_request_pending",
        "entity_join_requests",
        ["user_id", "entity_id"],
        unique=True,
        sqlite_where=sa.text("status = 'pending'"),
        postgresql_where=sa.text("status = 'pending'"),
    )
    op.create_index(
        "ix_entity_join_requests_entity_status",
        "entity_join_requests", ["entity_id", "status"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_entity_join_requests_entity_status", table_name="entity_join_requests"
    )
    op.drop_index(
        "uq_entity_join_request_pending", table_name="entity_join_requests"
    )
    op.drop_table("entity_join_requests")
