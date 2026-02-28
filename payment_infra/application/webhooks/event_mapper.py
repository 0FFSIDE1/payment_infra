"""
Module for mapping raw webhook payloads from payment providers to a standardized internal format. This allows the application to process webhook events in a consistent way regardless of the provider's specific payload structure. The mapper extracts relevant information such as event type, reference, email, amount, and currency, and normalizes it for use in the application's domain logic.
"""
from decimal import Decimal


class PaystackEventMapper:

    @staticmethod
    def map(payload: dict) -> dict:
        event = payload.get("event")
        data = payload.get("data", {})

        base = {
            "event": event,
            "reference": data.get("reference"),
            "invoice_code": data.get("invoice_code"),
            "subscription_code": (
                data.get("subscription", {}).get("subscription_code")
                if data.get("subscription") else None
            ),
            "email": (
                data.get("customer", {}).get("email")
                if data.get("customer") else data.get("email")
            ),
            "amount": (
                Decimal(data["amount"]) / 100
                if data.get("amount") else None
            ),
            "currency": data.get("currency"),
            "raw": payload,
        }

        if event == "charge.success":
            base["type"] = "payment.success"

        elif event == "charge.failed":
            base["type"] = "payment.failed"

        elif event == "subscription.create":
            base["type"] = "subscription.created"

        else:
            base["type"] = "unknown"

        return base