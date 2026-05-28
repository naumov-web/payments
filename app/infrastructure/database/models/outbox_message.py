from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[UUID] = (
        mapped_column(
            UUID(as_uuid=True),
            primary_key=True,
            default=uuid4,
        )
    )

    topic: Mapped[str] = (
        mapped_column(
            String(255),
            nullable=False,
            index=True,
        )
    )

    payload: Mapped[dict] = (
        mapped_column(
            JSONB,
            nullable=False,
        )
    )

    status: Mapped[str] = (
        mapped_column(
            String(50),
            nullable=False,
            default="PENDING",
            index=True,
        )
    )

    created_at: Mapped[datetime] = (
        mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
            index=True,
        )
    )

    processed_at: (
        Mapped[datetime | None]
    ) = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )