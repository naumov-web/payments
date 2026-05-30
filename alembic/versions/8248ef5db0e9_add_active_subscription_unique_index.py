"""add active subscription unique index

Revision ID: 8248ef5db0e9
Revises: 85c67f72a5cc
Create Date: 2026-05-29 23:34:10.632403

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8248ef5db0e9'
down_revision: Union[str, Sequence[str], None] = '85c67f72a5cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE UNIQUE INDEX uq_active_subscription
        ON subscriptions (
            subscriber_actor_id,
            service_actor_id
        )
        WHERE status = 'ACTIVE'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS uq_active_subscription
        """
    )
