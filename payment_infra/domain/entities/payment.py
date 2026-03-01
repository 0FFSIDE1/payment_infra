"""
Defines the Payment entity and related value objects. The Payment entity represents a payment transaction in the system, encapsulating all relevant information such as amount, currency, status, and timestamps. This module also defines the PaymentStatus enum to represent the various states a payment can be in (e.g. pending, processing, success, failed). The Payment entity is designed to be immutable and is used throughout the application to represent payment data in a consistent way.
"""
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