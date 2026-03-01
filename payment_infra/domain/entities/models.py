"""
Module for the payment models. This module defines the Payment and PaymentWebhookLog models, which represent the core data structures for handling payments and logging webhook events in the application. The Payment model includes fields for tracking the amount, currency, email, status, idempotency key, and timestamps for each payment transaction. The PaymentWebhookLog model captures details of incoming webhook events, including the event type, associated invoice or subscription codes, payload data, signature validation status, and processing status. These models are essential for maintaining a record of payment transactions and webhook interactions, enabling robust tracking and auditing of payment-related activities within the system.
"""
import uuid
from django.db import models


class Payment(models.Model):

    class Status(models.TextChoices):
        PENDING = "PENDING"
        PROCESSING = "PROCESSING"
        SUCCESS = "SUCCESS"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10)
    email = models.EmailField(null=False, blank=False)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    idempotency_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "created_at", "idempotency_key", "email"]),
        ]

class PaymentWebhookLog(models.Model):

    event = models.CharField(max_length=100)
    invoice_code = models.CharField(max_length=100, blank=True, null=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    subscription_code = models.CharField(max_length=100, blank=True, null=True)
    received_at = models.DateTimeField(auto_now_add=True)
    payload = models.JSONField()
    valid_signature = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    extra_info = models.CharField(max_length=255, default=None, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["event", "reference"],
                name="unique_webhook_event_reference"
            )
        ]

    def __str__(self):
        return f"{self.event} at {self.received_at}"
        