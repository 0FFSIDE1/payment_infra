"""
Defines the IdempotencyKey model, which is used to store idempotency keys and their associated status and response payloads. This model is used by the idempotency service to track the processing of requests with idempotency keys, ensuring that duplicate requests are handled correctly and that the same response is returned for the same key. The model includes fields for the key, status, response payload, and timestamps for when the key was created and last locked. The status field uses a TextChoices enum to represent the different states a key can be in (e.g. started, processing, completed, failed). The model also includes an index on the status and key fields for efficient querying.
"""
import uuid
from django.db import models


class IdempotencyKey(models.Model):

    class Status(models.TextChoices):
        STARTED = "STARTED"
        PROCESSING = "PROCESSING"
        COMPLETED = "COMPLETED"
        FAILED = "FAILED"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.STARTED
    )

    response_payload = models.JSONField(null=True, blank=True)

    locked_at = models.DateTimeField(auto_now=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["status", "key"]),
        ]