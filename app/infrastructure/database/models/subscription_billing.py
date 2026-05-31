from datetime import datetime
from uuid import UUID
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class SubscriptionBillingModel(Base):
    __tablename__ = "subscription_billings"

    billing_id: Mapped[UUID] = (
        mapped_column(
            PG_UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
        )
    )

    subscription_id: Mapped[UUID] = (
        mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey(
                "subscriptions.subscription_id"
            ),
            nullable=False,
            index=True,
        )
    )

    transaction_id: Mapped[UUID] = (
        mapped_column(
            PG_UUID(as_uuid=True),
            nullable=False,
            unique=True,
        )
    )

    billing_date: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            nullable=False,
            index=True,
        )
    )

    status: Mapped[str] = (
        mapped_column(
            String(20),
            nullable=False,
            index=True,
        )
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )