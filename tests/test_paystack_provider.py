import pytest
from decimal import Decimal
from unittest.mock import patch
from django.conf import settings
from payment_infra.infrastructure.providers.paystack_provider import (
    PaystackProvider
)


@pytest.mark.django_db
@patch("payment_infra.infrastructure.providers.paystack_provider.requests.post")
def test_paystack_charge_success(mock_post, settings):

    settings.PAYSTACK_SECRET_KEY = "sk_test_xxx"

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "status": True,
        "message": "Authorization URL created",
        "data": {
            "authorization_url": "https://checkout.paystack.com/abc123",
            "reference": "ref123"
        }
    }

    provider = PaystackProvider()

    response = provider.charge(
        email="test@example.com",
        amount=Decimal("100.00"),
        currency="NGN",
        ref="ref123",
        callback_url=getattr(settings, "PAYSTACK_CALLBACK_URL", None)
    )

    assert response["status"] is True
    assert "authorization_url" in response["data"]

@patch("payment_infra.infrastructure.providers.paystack_provider.requests.post")
def test_paystack_charge_failure(mock_post, settings):

    settings.PAYSTACK_SECRET_KEY = "sk_test_xxx"

    mock_post.return_value.raise_for_status.side_effect = Exception("API error")

    provider = PaystackProvider()

    with pytest.raises(Exception):
        provider.charge(
            email="test@example.com",
            amount=Decimal("100.00"),
            ref="ref123",
            currency="NGN",
            callback_url=getattr(settings, "PAYSTACK_CALLBACK_URL", None)
        )