import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class TransactionsOrm(Base):
    __tablename__ = 'transactions'

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    payment_id: Mapped[uuid.UUID] = mapped_column(unique=True)
    amount: Mapped[Decimal]
    currency: Mapped[str]
    status: Mapped[str]
    event_type: Mapped[str]
    processed_at: Mapped[datetime]
