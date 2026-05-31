"""add retry_after to subscriptions

Revision ID: 46e796d6efe8
Revises: ad5443d69af6
Create Date: 2026-05-31 21:26:23.391422

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46e796d6efe8'
down_revision: Union[str, Sequence[str], None] = 'ad5443d69af6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "subscriptions",
        sa.Column(
            "retry_after",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_subscriptions_retry_after",
        "subscriptions",
        ["retry_after"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_subscriptions_retry_after",
        table_name="subscriptions",
    )

    op.drop_column(
        "subscriptions",
        "retry_after",
    )
