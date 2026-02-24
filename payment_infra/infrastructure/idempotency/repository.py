from payment_infra.infrastructure.idempotency.models import IdempotencyKey


class IdempotencyRepository:

    def get(self, key: str):
        try:
            return IdempotencyKey.objects.get(key=key)
        except IdempotencyKey.DoesNotExist:
            return None

    def create(self, key: str):
        return IdempotencyKey.objects.create(key=key)

    def mark_processing(self, key: str):
        IdempotencyKey.objects.filter(key=key).update(
            status=IdempotencyKey.Status.PROCESSING
        )

    def mark_completed(self, key: str, response_payload: dict):
        IdempotencyKey.objects.filter(key=key).update(
            status=IdempotencyKey.Status.COMPLETED,
            response_payload=response_payload
        )

    def mark_failed(self, key: str):
        IdempotencyKey.objects.filter(key=key).update(
            status=IdempotencyKey.Status.FAILED
        )