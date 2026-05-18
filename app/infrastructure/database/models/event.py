from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class EventModel(Base):
    __tablename__ = "events"

    __table_args__ = (
        UniqueConstraint(
            "aggregate_id",
            "stream_version",
            name="uq_aggregate_stream_version",
        ),
    )

    event_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    aggregate_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        nullable=False,
        index=True,
    )

    aggregate_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    stream_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    event_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )

    event_version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )

    payload: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
    )

    event_metadata: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )