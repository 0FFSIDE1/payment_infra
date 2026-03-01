"""
Module for the IdempotencyService, which provides a way to execute functions in an idempotent-safe way. This service uses the IdempotencyRepository to track the status of requests with idempotency keys, ensuring that duplicate requests are handled correctly and that the same response is returned for the same key. The service uses a distributed lock (implemented with Redis) to ensure that only one process can handle a request with a given key at a time, preventing race conditions and ensuring data consistency. The `execute` method checks the status of the key, acquires a lock, and then executes the callback function while updating the status of the key accordingly (processing, completed, failed).
"""

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