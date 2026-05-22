from sqlalchemy import DateTime
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

from app.infrastructure.database.base import Base


class IdempotencyKeyModel(Base):
    __tablename__ = "idempotency_keys"

    idempotency_key: Mapped[str] = (
        mapped_column(
            String(255),
            primary_key=True,
        )
    )

    operation_type: Mapped[str] = (
        mapped_column(
            String(100),
            nullable=False,
        )
    )

    request_hash: Mapped[str] = (
        mapped_column(
            String(64),
            nullable=False,
        )
    )

    response_payload: Mapped[dict] = (
        mapped_column(
            JSONB,
            nullable=False,
        )
    )

    created_at: Mapped[DateTime] = (
        mapped_column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False,
        )
    )