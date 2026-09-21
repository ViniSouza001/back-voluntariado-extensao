"""Create notifications table.

Revision ID: a13d86c29f04
Revises: e82f10a47c61
"""

from alembic import op
import sqlalchemy as sa


revision = "a13d86c29f04"
down_revision = "e82f10a47c61"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column(
            "notification_type",
            sa.Enum(
                "invitation_received",
                "invitation_accepted",
                "invitation_rejected",
                "entity_member_joined",
                "entity_member_left",
                "entity_role_changed",
                "entity_member_removed",
                "vacancy_created",
                "vacancy_updated",
                "vacancy_deleted",
                "vacancy_participant_joined",
                "vacancy_participant_left",
                "vacancy_participant_removed",
                name="notification_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("message", sa.String(length=255), nullable=False),
        sa.Column("invitation_id", sa.Integer(), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("vacancy_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=False), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=False), nullable=True),
        sa.Column("archived_at", sa.DateTime(timezone=False), nullable=True),
        sa.CheckConstraint(
            "(invitation_id IS NULL OR entity_id IS NULL) AND "
            "(invitation_id IS NULL OR vacancy_id IS NULL) AND "
            "(entity_id IS NULL OR vacancy_id IS NULL)",
            name="ck_notification_single_resource",
        ),
        sa.ForeignKeyConstraint(
            ["actor_id"], ["users.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["entity_id"], ["entities.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["invitation_id"], ["invitations.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["recipient_id"], ["users.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["vacancy_id"], ["vacancies.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_notifications_recipient_archived_created",
        "notifications",
        ["recipient_id", "archived_at", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_notifications_recipient_archived_created",
        table_name="notifications",
    )
    op.drop_table("notifications")
