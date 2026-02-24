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