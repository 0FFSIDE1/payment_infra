"""
Defines abstract interfaces for repositories. These interfaces define the contract for how the application interacts with the data layer, allowing for flexibility in choosing different storage implementations (e.g. SQL, NoSQL, in-memory) without affecting the business logic.
"""

from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional
from payment_infra.domain.entities.payment import Payment


class AbstractPaymentRepository(ABC):

    @abstractmethod
    def create(self, payment: Payment) -> Payment:
        pass

    @abstractmethod
    def get_by_idempotency_key(self, key: str) -> Optional[Payment]:
        pass

    @abstractmethod
    def update_status(self, payment_id: UUID, status: str):
        pass