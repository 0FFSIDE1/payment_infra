from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Dict


class AbstractPaymentProvider(ABC):

    @abstractmethod
    def charge(
        self,
        email: str,
        ref: str,
        amount: Decimal,
        currency: str,
        metadata: Dict,
        callback_url: str
    ) -> Dict:
        pass

    @abstractmethod
    def verify(self, reference: str) -> Dict:
        pass


class AbstractWebhookProvider(ABC):

    @abstractmethod
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        pass

    @abstractmethod
    def parse_event(self, payload: dict) -> dict:
        pass