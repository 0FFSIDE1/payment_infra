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