import json
import hmac
import hashlib
import pytest
from django.conf import settings
from rest_framework.test import APIClient
from django.test import override_settings

@pytest.mark.django_db
def test_webhook_valid_signature():
    from payment_infra.domain.entities.models import PaymentWebhookLog
    client = APIClient()

    payload = {
        "event": "charge.success",
        "data": {
            "reference": "ref-123",
            "amount": 10000,
            "currency": "NGN"
        }
    }

    raw_body = json.dumps(payload).encode()

    signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        raw_body,
        hashlib.sha512
    ).hexdigest()

    response = client.post(
        "/webhooks/",
        data=raw_body,
        content_type="application/json",
        HTTP_X_PAYSTACK_SIGNATURE=signature
    )

    assert response.status_code == 200
    assert response.data["message"] == "Webhook received"

    # Ensure log created
    assert PaymentWebhookLog.objects.count() == 1
    log = PaymentWebhookLog.objects.first()
    assert log.valid_signature is True
    assert log.event == "charge.success"

@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_THROTTLE_RATES": {
            "webhook": "29/minute",
        },
    }
)
@pytest.mark.django_db
def test_webhook_throttling():

    client = APIClient()

    payload = {"event": "charge.success"}
    raw_body = json.dumps(payload).encode()

    signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        raw_body,
        hashlib.sha512
    ).hexdigest()

    for i in range(30):
        response = client.post(
            "/webhooks/",
            data=raw_body,
            content_type="application/json",
            HTTP_X_PAYSTACK_SIGNATURE=signature
        )
        assert response.status_code == 200

    # 31st request should be throttled
    response = client.post(
        "/webhooks/",
        data=raw_body,
        content_type="application/json",
        HTTP_X_PAYSTACK_SIGNATURE=signature
    )

    assert response.status_code == 429


@pytest.mark.django_db
def test_webhook_idempotency_prevents_duplicate_processing():
    from payment_infra.domain.entities.models import PaymentWebhookLog
    client = APIClient()

    payload = {
        "event": "charge.success",
        "data": {
            "reference": "dup-ref-123",
            "amount": 10000,
            "currency": "NGN"
        }
    }

    raw_body = json.dumps(payload).encode()

    signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        raw_body,
        hashlib.sha512
    ).hexdigest()

    # First webhook call
    response1 = client.post(
        "/webhooks/",
        data=raw_body,
        content_type="application/json",
        HTTP_X_PAYSTACK_SIGNATURE=signature
    )

    assert response1.status_code == 200
    assert response1.data["event"]["status"] == "processed"

    assert PaymentWebhookLog.objects.count() == 1

    # Second (duplicate) webhook call
    response2 = client.post(
        "/webhooks/",
        data=raw_body,
        content_type="application/json",
        HTTP_X_PAYSTACK_SIGNATURE=signature
    )

    assert response2.status_code == 200
    assert response2.data["event"]["status"] == "duplicate"

    # Still only one record in DB
    assert PaymentWebhookLog.objects.count() == 1