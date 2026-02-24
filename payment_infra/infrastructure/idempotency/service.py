from django.db import transaction
from payment_infra.infrastructure.idempotency.repository import (
    IdempotencyRepository
)
from payment_infra.infrastructure.idempotency.lock import redis_lock
from payment_infra.infrastructure.idempotency.models import IdempotencyKey

class IdempotencyService:

    def __init__(self):
        self.repository = IdempotencyRepository()

    def execute(self, key: str, callback):
        """
        Executes a function in an idempotent-safe way.
        """

        existing = self.repository.get(key)

        if existing:
            if existing.status == IdempotencyKey.Status.COMPLETED:
                return existing.response_payload

            if existing.status == IdempotencyKey.Status.PROCESSING:
                raise RuntimeError("Request already processing.")

        with redis_lock(key):

            with transaction.atomic():

                record = self.repository.get(key)

                if record and record.status == IdempotencyKey.Status.COMPLETED:
                    return record.response_payload

                if not record:
                    record = self.repository.create(key)

                self.repository.mark_processing(key)

                try:
                    result = callback()

                    self.repository.mark_completed(key, result)

                    return result

                except Exception:
                    self.repository.mark_failed(key)
                    raise