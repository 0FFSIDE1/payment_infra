"""
Service layer for handling payment webhooks. Responsible for:
- Verifying webhook signatures
- Mapping provider-specific events to internal format
- Logging webhook events (valid and invalid)
- Triggering domain events based on webhook data (e.g. updating payment status)
"""

import json
from payment_infra.domain.entities.models import PaymentWebhookLog
from payment_infra.application.webhooks.event_mapper import PaystackEventMapper
from django.db import transaction, IntegrityError

class WebhookService:

    def __init__(self, provider, mapper):
        self.provider = provider
        self.mapper = mapper

    def handle(self, raw_body: bytes, signature: str):
        """
        Handles incoming webhook:
        1. Verifies signature
        2. Maps event data to internal format
        3. Logs the event (valid or invalid)
        4. Returns mapped event data for further processing
        """
        if not signature:
            raise ValueError("Missing signature")

        if not self.provider.verify_signature(raw_body, signature):
            self._log_invalid(raw_body)
            raise ValueError("Invalid signature")

        payload = json.loads(raw_body)

        mapped_event = self.mapper.map(payload)

        result = self._log_valid(mapped_event)

        # Future: trigger domain events here
        # e.g. update payment status

        return result

    def _log_valid(self, event_data: dict):
        """
        Logs valid webhook events to the database. Uses a transaction to ensure atomicity.
        """
        try:
            with transaction.atomic():
                log = PaymentWebhookLog.objects.create(
                    event=event_data["event"],
                    reference=event_data.get("reference"),
                    invoice_code=event_data.get("invoice_code"),
                    subscription_code=event_data.get("subscription_code"),
                    payload=event_data["raw"],
                    valid_signature=True,
                    processed=True,
                )

            return {
                "status": "processed",
                "event": event_data,
            }

        except IntegrityError:
            # Duplicate webhook — already processed
            return {
                "status": "duplicate",
                "event": event_data["event"],
            }

    def _log_invalid(self, raw_body: bytes):
        """
        Logs invalid webhook attempts (e.g. signature verification failures) for auditing and security monitoring.
        """
        PaymentWebhookLog.objects.create(
            event="invalid_signature",
            payload=json.loads(raw_body),
            valid_signature=False,
            processed=False,
        )