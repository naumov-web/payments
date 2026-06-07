from datetime import datetime
from uuid import UUID
from uuid import uuid4

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func
from sqlalchemy import Enum

from app.infrastructure.database.base import Base
from app.domain.subscriptions.subscription_status import SubscriptionStatus

class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    subscription_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    subscriber_actor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("actors.actor_id"),
        nullable=False,
        index=True,
    )

    service_actor_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("actors.actor_id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    billing_period: Mapped[str] =mapped_column(
        String(20),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=SubscriptionStatus.ACTIVE.value,
        index=True,
    )

    next_billing_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    retry_after: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )