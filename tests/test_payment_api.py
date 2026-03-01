import pytest
from rest_framework.test import APIClient
import random
import os
from django.conf import settings

pytestmark = [
    pytest.mark.django_db,
    pytest.mark.integration,
]
def test_real_paystack_payment():
    from payment_infra.infrastructure.idempotency.models import IdempotencyKey

    client = APIClient()

    response = client.post(
        "/paystack/charge/",
        {
            "email": "test@test.com",
            "amount": "100.00",
            "currency": "NGN",
            "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
        },
        format="json",
    )

    assert response.status_code == 200
    assert "reference" in response.data


def test_real_paystack_payment_idempotency():
    client = APIClient()

    key = f"real-test-{random.randint(1000, 9999)}"

    first_response = client.post(
        "/paystack/charge/",
        {
            "email": "test@example.com",
            "amount": "100.00",
            "currency": "NGN",
            "idempotency_key": key,
            "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
        },
        format="json",
    )

    assert first_response.status_code == 200
    assert "reference" in first_response.data

    second_response = client.post(
        "/paystack/charge/",
        {
            "email": "test@example.com",
            "amount": "100.00",
            "currency": "NGN",
            "idempotency_key": key,
            "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
        },
        format="json",
    )

    assert second_response.status_code == 200
    assert second_response.data == first_response.data


def test_real_paystack_payment_creates_unique_transactions():
    client = APIClient()

    payload = {
        "email": "test@example.com",
        "amount": "100.00",
        "currency": "NGN",
        "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
    }

    first_response = client.post(
        "/paystack/charge/",
        payload,
        format="json",
    )

    assert first_response.status_code == 200
    assert "reference" in first_response.data

    second_response = client.post(
        "/paystack/charge/",
        payload,
        format="json",
    )

    assert second_response.status_code == 200
    assert "reference" in second_response.data

    # Ensure they are different transactions
    assert first_response.data["reference"] != second_response.data["reference"]
    assert first_response.data["access_code"] != second_response.data["access_code"]


def test_real_verify_payment():
    client = APIClient()

    charge_response = client.post(
        "/paystack/charge/",
        {
            "email": "test@example.com",
            "amount": "100.00",
            "currency": "NGN",
            "callback_url": getattr(settings, "PAYSTACK_CALLBACK_URL", None),
        },
        format="json",
    )

    assert charge_response.status_code == 200

    reference = charge_response.data["reference"]

    verify_response = client.get(f"/paystack/verify/{reference}/")

    assert verify_response.status_code == 200
    assert "status" in verify_response.data


def test_idempotency_already_processing():
    from payment_infra.infrastructure.idempotency.models import IdempotencyKey
    from payment_infra.infrastructure.idempotency.service import IdempotencyService

    key = "test-processing-key"
    # Create a processing record manually
    IdempotencyKey.objects.create(
        key=key,
        status=IdempotencyKey.Status.PROCESSING,
    )

    service = IdempotencyService()

    def dummy_callback():
        return {"ok": True}

    with pytest.raises(RuntimeError, match="Request already processing"):
        service.execute(key, dummy_callback)


def test_idempotency_returns_existing_completed_result():
    from payment_infra.infrastructure.idempotency.models import IdempotencyKey
    from payment_infra.infrastructure.idempotency.service import IdempotencyService

    key = "test-completed-key"

    IdempotencyKey.objects.create(
        key=key,
        status=IdempotencyKey.Status.COMPLETED,
        response_payload={"cached": True},
    )

    service = IdempotencyService()

    def callback():
        pytest.fail("Callback should not be executed")

    result = service.execute(key, callback)

    assert result == {"cached": True}


def test_idempotency_retry_after_failure():
    from payment_infra.infrastructure.idempotency.models import IdempotencyKey
    from payment_infra.infrastructure.idempotency.service import IdempotencyService

    key = "test-failed-key"

    IdempotencyKey.objects.create(
        key=key,
        status=IdempotencyKey.Status.FAILED,
    )

    service = IdempotencyService()

    def callback():
        return {"retried": True}

    result = service.execute(key, callback)

    assert result == {"retried": True}

    updated = IdempotencyKey.objects.get(key=key)
    assert updated.status == IdempotencyKey.Status.COMPLETED