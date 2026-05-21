from sqlalchemy import BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from app.infrastructure.database.base import Base


class WalletBalanceModel(Base):
    __tablename__ = "wallet_balances"

    actor_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
    )

    balance: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
    )