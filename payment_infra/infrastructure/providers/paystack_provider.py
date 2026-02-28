"""
Module for the Paystack payment provider implementation. This module defines the PaystackProvider class, which implements the AbstractPaymentProvider and AbstractWebhookProvider interfaces. The PaystackProvider class provides methods for charging a customer, verifying a transaction, and verifying webhook signatures. It uses the Paystack API to perform these operations, and handles the necessary authentication and request formatting. The provider also includes error handling to raise exceptions for any issues that occur during API calls.
"""
import requests
from decimal import Decimal
from django.conf import settings
from payment_infra.application.interfaces.providers import AbstractPaymentProvider, AbstractWebhookProvider
from payment_infra.models import PaymentWebhookLog
import hmac
import hashlib

class PaystackProvider(AbstractPaymentProvider, AbstractWebhookProvider):

    def __init__(self):
        self.base_url = getattr(
            settings,
            "PAYSTACK_BASE_URL",
            "https://api.paystack.co"
        )

        self.secret_key = getattr(settings, "PAYSTACK_SECRET_KEY", None)
        self.public_key = getattr(settings, "PAYSTACK_PUBLIC_KEY", None)

        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

        self.timeout = 15

    def charge(
        self,
        email: str,
        amount: Decimal,
        ref: str,
        currency: str,
        callback_url: str,
        plan_code: str = None,
        metadata: dict = None
    ):
        data = {
            "email": email or metadata.get("email"),
            "amount": int(amount * 100),  # convert to kobo
            "currency": currency,
            "reference": ref,
            "callback_url": callback_url,
        }

        if plan_code:
            data["plan"] = plan_code

        url = f"{self.base_url}/transaction/initialize"

        response = requests.post(
            url,
            json=data,
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()
    
    def verify(self, reference: str):
        url = f"{self.base_url}/transaction/verify/{reference}"

        response = requests.get(
            url,
            headers=self.headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response.json()
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        computed = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            payload,
            hashlib.sha512
        ).hexdigest()

        return hmac.compare_digest(computed, signature)    