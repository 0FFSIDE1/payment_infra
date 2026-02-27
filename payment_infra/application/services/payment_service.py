from uuid import uuid4
from decimal import Decimal
from datetime import datetime

from django.db import transaction

from payment_infra.domain.entities.payment import (
    Payment,
    PaymentStatus
)

class PaymentService:

    def __init__(self, repository, provider, idempotency_service, mapper=None):
        self.repository = repository
        self.provider = provider
        self.idempotency = idempotency_service
        self.mapper = mapper

    def process_payment(
        self,
        email: str,
        amount: Decimal,
        currency: str,
        idempotency_key: str,
        metadata: dict = None
    ):
        """
        Fully idempotent and concurrency-safe payment execution.
        """

        def core_logic():
            # STEP 1: Create Payment record (short DB transaction)
            payment = self._create_payment_record(
                email,
                amount,
                currency,
                idempotency_key,
                metadata.get('callback_url') or None
            )

            # STEP 2: Call external provider (NO DB LOCK)
            response = self._charge_provider(
                payment,
                metadata or {}
            )

            # STEP 3: Update final state
            self._finalize_payment(payment.id, response)
            return {
                "payment_id": str(payment.id),
                "status": response.get("status", False),
                "authorization_url": response.get("data", {}).get("authorization_url"),
                "reference": response.get("data", {}).get("reference"),
                "message": response.get("message", ""),
                "access_code": response.get("data", {}).get("access_code"),
                "public_key": self.provider.public_key,               
            }

        return self.idempotency.execute(idempotency_key, core_logic)

    def verify_payment(self, idempotency_key: str):
        response = self.provider.verify(idempotency_key)

        payment = self.repository.get_by_idempotency_key(idempotency_key)

        if not response.get("status"):
            return {
                "payment_id": None,
                "status": False,
                "message": "Payment verification failed."
            }

        return {
            "payment_id": str(payment.id),
            "status": True,
            "message": "Payment verified successfully.",
            "amount": payment.amount,
            "currency": payment.currency,
            "reference": payment.idempotency_key
        }

    # INTERNAL METHODS
    @transaction.atomic
    def _create_payment_record(self, email, amount, currency, idempotency_key, callback_url):
        existing = self.repository.get_by_idempotency_key(idempotency_key)

        if existing:
            return existing

        payment = Payment(
            id=uuid4(),
            email=email,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            idempotency_key=idempotency_key,
            created_at=datetime.utcnow(),
            callback_url=callback_url
        )

        self.repository.create(payment)

        self.repository.update_status(
            payment.id,
            PaymentStatus.PROCESSING
        )

        return payment

    def _charge_provider(self, payment, metadata):
        return self.provider.charge(
            amount=payment.amount,
            ref=str(payment.idempotency_key),
            email=payment.email,
            currency=payment.currency,
            metadata=metadata,
            callback_url=metadata.get('callback_url') or payment.callback_url
        )

    @transaction.atomic
    def _finalize_payment(self, payment_id, response):
        if response.get("status"):
            self.repository.update_status(
                payment_id,
                PaymentStatus.SUCCESS
            )
        else:
            self.repository.update_status(
                payment_id,
                PaymentStatus.FAILED
            )