"""${message}

Identificador da revisão: ${up_revision}
Revisão anterior: ${down_revision | comma,n}
Data de criação: ${create_date}

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
${imports if imports else ""}

# Identificadores de revisão utilizados pelo Alembic.
revision: str = ${repr(up_revision)}
down_revision: str | Sequence[str] | None = ${repr(down_revision)}
branch_labels: str | Sequence[str] | None = ${repr(branch_labels)}
depends_on: str | Sequence[str] | None = ${repr(depends_on)}


def upgrade() -> None:
    """Aplica as alterações desta revisão."""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Desfaz as alterações desta revisão."""
    ${downgrades if downgrades else "pass"}
