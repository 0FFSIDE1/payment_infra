import pytest
from decimal import Decimal
from unittest.mock import MagicMock

from payment_infra.application.services.payment_service import PaymentService
from payment_infra.infrastructure.repositories.repository import PaymentRepository
from payment_infra.infrastructure.idempotency.in_memory import (
    InMemoryIdempotencyService
)
from django.conf import settings

idempotency = InMemoryIdempotencyService()

@pytest.mark.django_db
def test_payment_service_success(settings):

    mock_provider = MagicMock()
    mock_provider.charge.return_value = {"status": True}

    repository = PaymentRepository()

    service = PaymentService(
        repository=repository,
        provider=mock_provider,
        idempotency_service=idempotency
    )

    result = service.process_payment(
        amount=Decimal("200.00"),
        email="test@example.com",
        currency="NGN",
        idempotency_key="unique-key-123",
        metadata={"email": "test@example.com"}
    )

    assert result["status"] is True


@pytest.mark.django_db
def test_idempotent_payment(settings):

    mock_provider = MagicMock()
    mock_provider.charge.return_value = {"status": True}

    repository = PaymentRepository()
    service = PaymentService(repository, mock_provider, idempotency)

    key = "idem-key-001"

    first = service.process_payment(
        amount=Decimal("100.00"),
        email="test@example.com",
        currency="NGN",
        idempotency_key=key,
        metadata={
            "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
        }
    )

    second = service.process_payment(
        amount=Decimal("100.00"),
        email="test@example.com",
        currency="NGN",
        idempotency_key=key,
        metadata={
            "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
        }
    )

    assert first == second
    assert mock_provider.charge.call_count == 1