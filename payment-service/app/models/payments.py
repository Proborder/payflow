import enum
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import Enum, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StatusEnum(enum.StrEnum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class PaymentsOrm(Base):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=10, scale=2))
    currency: Mapped[str] = mapped_column(String(3))
    status: Mapped[StatusEnum] = mapped_column(Enum(StatusEnum, native_enum=True), default=StatusEnum.PENDING)
    description: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())
    idempotency_key: Mapped[uuid.UUID] = mapped_column(unique=True)
