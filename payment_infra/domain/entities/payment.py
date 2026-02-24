from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from uuid import UUID
from datetime import datetime


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


@dataclass(frozen=True)
class Payment:
    id: UUID
    email: str
    amount: Decimal
    currency: str
    status: PaymentStatus
    idempotency_key: str
    created_at: datetime
    callback_url: str