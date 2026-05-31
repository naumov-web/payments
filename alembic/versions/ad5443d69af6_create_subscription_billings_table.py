"""create subscription billings table

Revision ID: ad5443d69af6
Revises: 8248ef5db0e9
Create Date: 2026-05-31 21:17:01.438463

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'ad5443d69af6'
down_revision: Union[str, Sequence[str], None] = '8248ef5db0e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription_billings",

        sa.Column(
            "billing_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "subscription_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),

        sa.Column(
            "transaction_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),

        sa.Column(
            "billing_date",
            sa.DateTime(timezone=True),
            nullable=False,
        ),

        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),

        sa.ForeignKeyConstraint(
            ["subscription_id"],
            ["subscriptions.subscription_id"],
        ),

        sa.PrimaryKeyConstraint(
            "billing_id",
        ),
    )

    op.create_index(
        "ix_subscription_billings_subscription_id",
        "subscription_billings",
        ["subscription_id"],
    )

    op.create_index(
        "ix_subscription_billings_billing_date",
        "subscription_billings",
        ["billing_date"],
    )

    op.create_index(
        "ix_subscription_billings_status",
        "subscription_billings",
        ["status"],
    )

    op.create_unique_constraint(
        "uq_subscription_billings_transaction_id",
        "subscription_billings",
        ["transaction_id"],
    )

    op.create_unique_constraint(
        "uq_subscription_billings_period",
        "subscription_billings",
        [
            "subscription_id",
            "billing_date",
        ],
    )

def downgrade() -> None:
    op.drop_constraint(
        "uq_subscription_billings_period",
        "subscription_billings",
        type_="unique",
    )

    op.drop_constraint(
        "uq_subscription_billings_transaction_id",
        "subscription_billings",
        type_="unique",
    )

    op.drop_index(
        "ix_subscription_billings_status",
        table_name="subscription_billings",
    )

    op.drop_index(
        "ix_subscription_billings_billing_date",
        table_name="subscription_billings",
    )

    op.drop_index(
        "ix_subscription_billings_subscription_id",
        table_name="subscription_billings",
    )

    op.drop_table(
        "subscription_billings",
    )
