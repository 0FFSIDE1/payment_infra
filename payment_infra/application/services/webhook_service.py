import json
from payment_infra.models import PaymentWebhookLog
from payment_infra.application.webhooks.event_mapper import PaystackEventMapper
from django.db import transaction, IntegrityError

class WebhookService:

    def __init__(self, provider, mapper):
        self.provider = provider
        self.mapper = mapper

    def handle(self, raw_body: bytes, signature: str):

        if not signature:
            raise ValueError("Missing signature")

        if not self.provider.verify_signature(raw_body, signature):
            self._log_invalid(raw_body)
            raise ValueError("Invalid signature")

        payload = json.loads(raw_body)

        mapped_event = self.mapper.map(payload)

        self._log_valid(mapped_event)

        # Future: trigger domain events here
        # e.g. update payment status

        return {
            "status": "processed",
            "event": mapped_event
        }

    def _log_valid(self, event_data: dict):
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
                
        except IntegrityError:
            # Duplicate webhook — already processed
            return {
                "status": "duplicate",
                "event": event_data["event"],
            }

    def _log_invalid(self, raw_body: bytes):
        PaymentWebhookLog.objects.create(
            event="invalid_signature",
            payload=json.loads(raw_body),
            valid_signature=False,
            processed=False,
        )