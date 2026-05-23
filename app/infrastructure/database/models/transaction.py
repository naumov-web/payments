from datetime import datetime
from uuid import UUID

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[UUID] = (
        mapped_column(
            PG_UUID(as_uuid=True),
            primary_key=True,
        )
    )

    transaction_type: Mapped[str] = (
        mapped_column(
            String(100),
            nullable=False,
            index=True,
        )
    )

    sender_actor_id: Mapped[UUID] = (
        mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("actors.actor_id"),
            nullable=False,
            index=True,
        )
    )

    receiver_actor_id: Mapped[UUID] = (
        mapped_column(
            PG_UUID(as_uuid=True),
            ForeignKey("actors.actor_id"),
            nullable=False,
            index=True,
        )
    )

    amount: Mapped[int] = (
        mapped_column(
            BigInteger,
            nullable=False,
        )
    )

    reference_transaction_id: (
        Mapped[UUID | None]
    ) = mapped_column(
        PG_UUID(as_uuid=True),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True,
        )
    )